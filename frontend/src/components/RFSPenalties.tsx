import { useState, useEffect } from "react";
import { SingleValue } from "react-select";
import AppSelect from "./AppSelect";
import { api } from "../config/api";
import DataTable, { IColumn } from "./DataTable";
import FilterCard, { FilterField } from "./FilterCard";
import PageHeader from "./PageHeader";
import { loadedOn } from "./tableHelpers";

interface IOption {
  value: string;
  label: string;
  load_time: Date;
}

interface IResult {
  competitor_name: string;
  competitor_country: string;
  task_number: number;
  task_description: string;
  task_penalty: number;
  competition_penalty: number;
  notes: string;
}

interface ICompetition {
  competition_id: string;
  competition_load_time: string;
  competition_url: string;
  competition_description: string;
}

export default function RFSPenalties() {
  const [options, setOptions] = useState<IOption[]>();
  const [selected, setSelected] = useState<SingleValue<IOption>>();
  const [result, setResult] = useState<IResult[]>([]);

  useEffect(() => {
    async function fetchData() {
      const { data } = await api.get("/competition/get_all_competitions");
      const results: IOption[] = [];
      const sorted_data = data.sort(
        (a: ICompetition, b: ICompetition) =>
          new Date(b.competition_load_time).getTime() -
          new Date(a.competition_load_time).getTime()
      );
      sorted_data.forEach((value: ICompetition) => {
        results.push({
          value: value.competition_id,
          label: value.competition_description,
          load_time: new Date(value.competition_load_time),
        });
      });
      setOptions(results);
    }
    fetchData();
  }, []);

  const handleChange = (selected: SingleValue<IOption>) => {
    async function fetchCompetitionData() {
      if (selected) {
        const { data } = await api.get(`/query/rfs_penalties?competition_id=${selected.value}`);
        const results: IResult[] = [];
        data.forEach((value: IResult) => {
          results.push({
            competitor_name: value.competitor_name,
            competitor_country: value.competitor_country,
            task_number: value.task_number,
            task_description: value.task_description,
            task_penalty: value.task_penalty,
            competition_penalty: value.competition_penalty,
            notes: value.notes,
          });
        });
        setResult(results);
      }
    }
    setSelected(selected);
    fetchCompetitionData();
  };

  const columns: IColumn<IResult>[] = [
    { header: "Pilot", kind: "text", primary: true, render: (r) => <strong>{r.competitor_name}</strong> },
    { header: "Country", kind: "text", render: (r) => r.competitor_country },
    { header: "Task", kind: "num", primary: true, render: (r) => <span className="rank-badge">{r.task_number}</span> },
    { header: "Description", kind: "text", render: (r) => r.task_description },
    {
      header: "Penalty",
      kind: "num",
      primary: true,
      // The headline number: most events penalise at competition level, so
      // showing the task penalty alone reads as "—" on nearly every row.
      render: (r) => <strong>{r.task_penalty + r.competition_penalty || "—"}</strong>,
    },
    { header: "Task Pen", kind: "num", render: (r) => r.task_penalty || "—" },
    { header: "Comp Pen", kind: "num", render: (r) => r.competition_penalty || "—" },
    { header: "Notes", kind: "notes", render: (r) => r.notes },
  ];

  const penaltyClass = (r: IResult) => {
    if (r.task_penalty + r.competition_penalty === 0) return "table-warning";
    return r.competitor_country === "Spain" ? "table-info" : "table-danger";
  };

  return (
    <div className="container py-3">
      <PageHeader title="RFS Penalties" subtitle={loadedOn(selected?.load_time)} />

      <FilterCard>
        <FilterField label="Competition" className="col-12">
          <AppSelect options={options} onChange={handleChange} placeholder="Select a competition..." />
        </FilterField>
      </FilterCard>

      {result.length > 0 && (
        <div className="d-flex flex-wrap gap-3 mb-2 small text-muted">
          <span><span className="badge bg-danger">&nbsp;</span> penalised</span>
          <span><span className="badge bg-info text-dark">&nbsp;</span> penalised, Spain</span>
          <span><span className="badge bg-warning text-dark">&nbsp;</span> flagged, no penalty</span>
        </div>
      )}

      <DataTable
        columns={columns}
        rows={result}
        rowKey={(_, index) => index}
        rowClassName={penaltyClass}
        empty={selected ? "No RFS penalties in this competition." : "Select a competition to see RFS penalties."}
      />
    </div>
  );
}
