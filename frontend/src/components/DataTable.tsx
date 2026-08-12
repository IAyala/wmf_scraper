import React, { useState } from "react";

export interface IColumn<T> {
  /** Header text, and the label shown beside the value in the phone layout. */
  header: string;
  /** How the cell is aligned and sized. */
  kind?: "num" | "text" | "notes";
  /**
   * Show this column on the collapsed summary line on phones. Keep it to two
   * or three per table: an identifier, a name and the headline number.
   */
  primary?: boolean;
  render: (row: T, index: number) => React.ReactNode;
}

interface IProps<T> {
  columns: IColumn<T>[];
  rows: T[];
  rowKey: (row: T, index: number) => React.Key;
  /** Extra classes per row, e.g. rank-1 or table-danger. */
  rowClassName?: (row: T, index: number) => string | undefined;
  /** Shown instead of the table when there is nothing to display. */
  empty: string;
}

const CELL_CLASS: Record<string, string> = {
  num: "col-num",
  text: "col-text",
  notes: "col-notes",
};

/**
 * One table for every results screen.
 *
 * Above 768px it is an ordinary Bootstrap table that scrolls inside its own
 * card if it is too wide. Below that, index.css restacks each row into a card:
 * the columns marked `primary` stay on a single summary line, and the rest are
 * revealed by the chevron, so a 100-row table is still a short scroll.
 */
export default function DataTable<T>({ columns, rows, rowKey, rowClassName, empty }: IProps<T>) {
  const [expanded, setExpanded] = useState<ReadonlySet<React.Key>>(new Set());

  if (rows.length === 0) {
    return <div className="empty-state">{empty}</div>;
  }

  const hasDetails = columns.some((column) => !column.primary);
  // The name column carries the summary line, so let it take the spare space.
  const growHeader = columns.find((column) => column.primary && column.kind !== "num")?.header;

  const toggle = (key: React.Key) =>
    setExpanded((current) => {
      const next = new Set(current);
      if (!next.delete(key)) next.add(key);
      return next;
    });

  const cellClass = (column: IColumn<T>) =>
    [
      CELL_CLASS[column.kind ?? "text"],
      column.primary ? "is-primary" : undefined,
      column.header === growHeader ? "is-grow" : undefined,
    ]
      .filter(Boolean)
      .join(" ");

  return (
    <div className="table-card">
      <div className="table-scroll">
        <table className="table table-hover data-table align-middle">
          <thead className="table-dark">
            <tr>
              {columns.map((column) => (
                <th key={column.header} className={cellClass(column)} scope="col">
                  {column.header}
                </th>
              ))}
              {hasDetails && <th className="row-toggle" aria-label="Details" />}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, index) => {
              const key = rowKey(row, index);
              const isOpen = expanded.has(key);
              return (
                <tr key={key} className={`${rowClassName?.(row, index) ?? ""} ${isOpen ? "is-open" : ""}`.trim()}>
                  {columns.map((column) => (
                    <td key={column.header} data-label={column.header} className={cellClass(column)}>
                      {column.render(row, index)}
                    </td>
                  ))}
                  {hasDetails && (
                    <td className="row-toggle">
                      <button
                        type="button"
                        className="row-toggle-button"
                        aria-expanded={isOpen}
                        aria-label={isOpen ? "Hide details" : "Show details"}
                        onClick={() => toggle(key)}
                      >
                        <span aria-hidden="true">{isOpen ? "▲" : "▼"}</span>
                      </button>
                    </td>
                  )}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
