// Small helper functions for talking to the Flask API.
// Every function returns the parsed JSON body.

const BASE_URL = "http://127.0.0.1:5000";

async function handle(response) {
  const data = await response.json();
  if (!response.ok) {
    // The Flask API always sends {"error": "..."} on failure.
    throw new Error(data.error || "Request failed");
  }
  return data;
}

export function getAllItems() {
  return fetch(`${BASE_URL}/inventory`).then(handle);
}

export function addItem(item) {
  return fetch(`${BASE_URL}/inventory`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(item),
  }).then(handle);
}

export function updateItem(id, changes) {
  return fetch(`${BASE_URL}/inventory/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(changes),
  }).then(handle);
}

export function deleteItem(id) {
  return fetch(`${BASE_URL}/inventory/${id}`, { method: "DELETE" }).then(handle);
}

export function searchExternal(name) {
  return fetch(`${BASE_URL}/external/search?name=${encodeURIComponent(name)}`).then(handle);
}

export function enhanceItem(id) {
  return fetch(`${BASE_URL}/inventory/${id}/enhance`, { method: "POST" }).then(handle);
}
