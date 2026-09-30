import { NUMBERS_PER_DRAW, TOTAL_NUMBERS } from './constants';

/** Returns a sorted draw of unique random numbers. */
export const randomDraw = (size = NUMBERS_PER_DRAW) => {
  const draw = [];
  while (draw.length < size) {
    const num = Math.floor(Math.random() * TOTAL_NUMBERS);
    if (!draw.includes(num)) draw.push(num);
  }
  return draw.sort((a, b) => a - b);
};

/** Counts how many times every number appears in a list of draws. */
export const frequencyRanking = (history) => {
  const frequency = Array(TOTAL_NUMBERS).fill(0);
  history.forEach(draw => draw.numbers.forEach(n => frequency[n]++));

  return frequency
    .map((count, num) => ({ num, count }))
    .sort((a, b) => b.count - a.count);
};
