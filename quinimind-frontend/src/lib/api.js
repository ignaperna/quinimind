/** Fetches a URL and returns its parsed JSON body, throwing on HTTP errors. */
export const fetchJson = async (url) => {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Request failed (${res.status}): ${url}`);
  return res.json();
};
