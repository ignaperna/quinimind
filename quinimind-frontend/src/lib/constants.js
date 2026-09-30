// Shared configuration and domain constants for the QuiniMind UI.

// Quini 6 draws six numbers out of 00-45.
export const NUMBERS_PER_DRAW = 6;
export const MAX_NUMBER = 45;
export const TOTAL_NUMBERS = MAX_NUMBER + 1;

// Base URL of the QuiniMind API (see api.py).
export const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

// Static JSON feed produced by the scraper on every deploy.
export const LATEST_DRAW_FEED = "./data.json";

// Modalities in draw order, with the feed key and the accent color of each one.
export const MODES = [
  { name: "Tradicional", key: "tradicional", color: "text-blue-400" },
  { name: "La Segunda", key: "laSegunda", color: "text-emerald-400" },
  { name: "Revancha", key: "revancha", color: "text-amber-400" },
  { name: "Siempre Sale", key: "siempreSale", color: "text-rose-400" },
];
