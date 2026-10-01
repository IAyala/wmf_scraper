/** Small shared bits used by the results screens. */

/** Subtitle line: when the selected competition was last loaded. */
export const loadedOn = (loadTime?: Date): string | undefined =>
  loadTime ? `Loaded ${loadTime.toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" })}` : undefined;

/** Join the row classes that apply, or nothing when none do. */
export const rowClasses = (...classes: (string | undefined)[]): string | undefined =>
  classes.filter(Boolean).join(" ") || undefined;

/**
 * Podium tint for the top three, and the blue highlight for Spanish
 * competitors, the same blue RFS Penalties uses.
 *
 * Both classes are returned when both apply. The blue always wins the row,
 * because spotting the Spanish pilots is the point of the colour, while the
 * medal survives on the position badge: a Spanish winner gets a blue row with
 * a gold badge.
 */
export const rankClass = (position: number, country?: string): string | undefined =>
  rowClasses(position <= 3 ? `rank-${position}` : undefined, country === "Spain" ? "table-info" : undefined);

/** The flight stamped on a task. Null throughout when it was never scraped. */
export interface IFlightStamp {
  flight_number: number | null;
  flight_date: string | null;
  flight_period: string | null;
}

/** One flight of a competition, as /query/flights_in_competition returns it. */
export interface IFlight extends IFlightStamp {
  flight_number: number;
  task_orders: number[];
}

/** "Flight 3 · 14 Aug 2026 AM" — the date is what a pilot remembers. */
export const flightLabel = (flight: IFlightStamp): string => {
  if (flight.flight_number === null) return "—";
  const flown = [
    flight.flight_date
      ? new Date(`${flight.flight_date}T00:00:00`).toLocaleDateString(undefined, { dateStyle: "medium" })
      : undefined,
    flight.flight_period ?? undefined,
  ]
    .filter(Boolean)
    .join(" ");
  return flown ? `Flight ${flight.flight_number} · ${flown}` : `Flight ${flight.flight_number}`;
};
