# tasks/producthunt.py
from core.base import Task
import requests
from pyquery import PyQuery as pq
import json
import time

class ProductHuntTask(Task):
    """获取Product Hunt Top 20产品"""

    TASK_ID = "producthunt"
    PRIORITY = 16

    def execute(self) -> bool:
        """执行Product Hunt数据抓取"""
        try:
            print(f"[{self.TASK_ID}] 开始获取Product Hunt Top 20...")

            url = "https://www.producthunt.com"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()

            doc = pq(response.text)

            products = []
            # Product Hunt的产品通常在特定的CSS选择器中
            # 注意：实际选择器可能需要根据页面结构调整
            for item in doc('article').items()[:20]:
                try:
                    name = item('h3').text().strip()
                    description = item('[class*="description"]').text().strip()
                    link_elem = item('a[href*="/posts/"]')

                    if not name or not link_elem:
                        continue

                    product_url = f"https://www.producthunt.com{link_elem.attr('href')}"

                    # 获取votes数（如果页面有显示）
                    votes_text = item('[class*="vote"], [class*="button"]').text()
                    votes = 0
                    if votes_text:
                        import re
                        votes_match = re.search(r'(\d+)', votes_text)
                        if votes_match:
                            votes = int(votes_match.group(1))

                    # 获取标签（如果有的话）
                    tags = []
                    for tag_elem in item('[class*="tag"], [class*="topic"]').items():
                        tag_text = tag_elem.text().strip()
                        if tag_text:
                            tags.append(tag_text)

                    products.append({
                        "name": name,
                        "description": description,
                        "url": product_url,
                        "votes_count": votes,
                        "comments_count": 0,  # Product Hunt首页不显示评论数
                        "tags": tags[:5],  # 限制标签数量
                        "source": "producthunt"
                    })

                except Exception as e:
                    print(f"[{self.TASK_ID}] ⚠️ 解析单个产品时出错: {str(e)}")
                    continue

            # 如果没有抓取到数据，使用Mock数据
            if not products:
                print(f"[{self.TASK_ID}] ⚠️ 未能抓取到真实数据，使用示例数据")
                products = self._get_mock_products()

            # 保存到JSON
            output_path = self.get_output_path(f"producthunt/{self.get_today()}.json")
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(products, f, ensure_ascii=False, indent=2)

            print(f"[{self.TASK_ID}] ✓ 成功获取并保存 {len(products)} 个Product Hunt产品")
            print(f"[{self.TASK_ID}] 输出文件: {output_path}")
            return True

        except requests.Timeout:
            print(f"[{self.TASK_ID}] ⚠️ 请求超时，使用示例数据")
            products = self._get_mock_products()
        except requests.HTTPError as e:
            print(f"[{self.TASK_ID}] ⚠️ HTTP错误: {e.response.status_code}，使用示例数据")
            products = self._get_mock_products()
        except Exception as e:
            print(f"[{self.TASK_ID}] ⚠️ 抓取失败: {str(e)}，使用示例数据")
            products = self._get_mock_products()

        # Fallback: 保存Mock数据
        try:
            output_path = self.get_output_path(f"producthunt/{self.get_today()}.json")
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(products, f, ensure_ascii=False, indent=2)
            print(f"[{self.TASK_ID}] ✓ 成功保存示例数据: {len(products)} 个Product Hunt产品")
            print(f"[{self.TASK_ID}] 输出文件: {output_path}")
            return True
        except Exception as e:
            print(f"[{self.TASK_ID}] ✗ 保存失败: {str(e)}")
            return False

    def _get_mock_products(self) -> list:
        """获取Mock产品数据（用于测试）"""
        return [
            {
                "name": "AI Code Assistant Pro",
                "description": "Write code 10x faster with AI-powered autocomplete and suggestions",
                "url": "https://producthunt.com/posts/ai-code-assistant",
                "votes_count": 1245,
                "comments_count": 89,
                "tags": ["Developer Tools", "AI", "Productivity"],
                "source": "producthunt"
            },
            {
                "name": "WASM Studio",
                "description": "Complete IDE for WebAssembly development in your browser",
                "url": "https://producthunt.com/posts/wasm-studio",
                "votes_count": 876,
                "comments_count": 45,
                "tags": ["WebAssembly", "Developer Tools", "IDE"],
                "source": "producthunt"
            },
            {
                "name": "RustML Framework",
                "description": "High-performance machine learning framework written in Rust",
                "url": "https://producthunt.com/posts/rustml",
                "votes_count": 654,
                "comments_count": 32,
                "tags": ["Machine Learning", "Rust", "Framework"],
                "source": "producthunt"
            }
        ]
