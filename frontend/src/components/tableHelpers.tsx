/** Small shared bits used by the results screens. */

/** Subtitle line: when the selected competition was last loaded. */
export const loadedOn = (loadTime?: Date): string | undefined =>
  loadTime ? `Loaded ${loadTime.toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" })}` : undefined;

/**
 * Podium tint for the top three, and the existing highlight for Spanish
 * competitors. The podium wins when both apply.
 */
export const rankClass = (position: number, country?: string): string | undefined => {
  if (position <= 3) return `rank-${position}`;
  if (country === "Spain") return "table-warning";
  return undefined;
};
