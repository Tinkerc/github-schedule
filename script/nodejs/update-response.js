/// This func is called if the Request Checkbox is Enabled. You can modify the Request Data here before the request hits to the server
/// e.g. Add/Update/Remove: host, scheme, port, path, headers, queries, comment, color and body (json, form, plain-text, base64 encoded string)
///
/// Use global object `sharedState` to share data between Requests/Response from different scripts (e.g. sharedState.data = "My-Data")
///
async function onRequest(context, url, request) {
  // console.log(request);
  console.log(url);

  // Update or Add new headers
  // request.headers["X-New-Headers"] = "My-Value";

  // Update or Add new queries
  // request.queries["name"] = "Proxyman";

  // Body
  // var body = request.body;
  // body["new-key"] = "new-value"
  // request.body = body;

  // Done
  return request;
}

/// This func is called if the Response Checkbox is Enabled. You can modify the Response Data here before it goes to the client
/// e.g. Add/Update/Remove: headers, statusCode, comment, color and body (json, plain-text, base64 encoded string)
///
async function onResponse(context, url, request, response) {
  // Parse the response body
  var body = response.body;
  
  // Check if the response has the expected structure
  if (body && body.data && Array.isArray(body.data)) {
    // Modify each user object in the data array
    body.data = body.data.map(user => {
      // Create a new date object for createdDate 2 years in the future
      const createdDate = new Date(user.createdDate);
      createdDate.setFullYear(createdDate.getFullYear() + 2);
      
      return {
        ...user,
        createdDate: createdDate.toISOString().replace('Z', '+08:00')
      };
    });
  }
  
  // Update the response body
  response.body = body;
  
  // Done
  return response;
}