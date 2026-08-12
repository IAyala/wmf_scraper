import React from "react";

interface IProps {
  title: string;
  /** Optional line under the title, e.g. when the competition was loaded. */
  subtitle?: string;
}

const PageHeader: React.FC<IProps> = ({ title, subtitle }) => (
  <div className="mb-3">
    <h1 className="page-title">{title}</h1>
    {subtitle && <p className="page-subtitle">{subtitle}</p>}
  </div>
);

export default PageHeader;
