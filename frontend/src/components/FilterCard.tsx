import React from "react";

interface IProps {
  children: React.ReactNode;
}

/** Groups the selects at the top of a screen into one panel. */
const FilterCard: React.FC<IProps> = ({ children }) => (
  <div className="filter-card mb-3">
    <div className="row g-3">{children}</div>
  </div>
);

interface IFieldProps {
  label: string;
  /** Bootstrap column classes. Defaults to full width on phones, half above. */
  className?: string;
  children: React.ReactNode;
}

export const FilterField: React.FC<IFieldProps> = ({ label, className = "col-12 col-md-6", children }) => (
  <div className={className}>
    <label className="filter-label">{label}</label>
    {children}
  </div>
);

export default FilterCard;
