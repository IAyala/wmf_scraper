import { useState, useEffect } from "react";
import { SingleValue } from "react-select";
import AppSelect from "./AppSelect";
import { api } from "../config/api";
import DataTable, { IColumn } from "./DataTable";
import FilterCard, { FilterField } from "./FilterCard";
import PageHeader from "./PageHeader";
import { loadedOn, rankClass } from "./tableHelpers";

interface IOption {
  value: string;
  label: string;
  load_time: Date;
}

interface IResult {
  total_score: number;
  average_score: number;
  total_competition_penalty: number;
  total_task_penalty: number;
  competitor_name: string;
  competitor_country: string;
  position: number;
}

interface ICompetition {
  competition_id: string;
  competition_load_time: string;
  competition_url: string;
  competition_description: string;
}

export default function CompetitionOveralls() {
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
        const { data } = await api.get(`/query/overall_results_competition?competition_id=${selected.value}`);
        const results: IResult[] = [];
        data.forEach((value: IResult) => {
          results.push({
            total_score: value.total_score,
            average_score: value.average_score,
            total_competition_penalty: value.total_competition_penalty,
            total_task_penalty: value.total_task_penalty,
            competitor_name: value.competitor_name,
            competitor_country: value.competitor_country,
            position: value.position,
          });
        });
        setResult(results);
      }
    }
    setSelected(selected);
    fetchCompetitionData();
  };

  const columns: IColumn<IResult>[] = [
    { header: "Pos", kind: "num", primary: true, render: (r) => <span className="rank-badge">{r.position}</span> },
    { header: "Competitor", kind: "text", primary: true, render: (r) => <strong>{r.competitor_name}</strong> },
    { header: "Country", kind: "text", render: (r) => r.competitor_country },
    { header: "Total", kind: "num", primary: true, render: (r) => <strong>{r.total_score.toLocaleString()}</strong> },
    { header: "Average", kind: "num", render: (r) => r.average_score.toLocaleString() },
    { header: "Comp Pen", kind: "num", render: (r) => r.total_competition_penalty },
    { header: "Task Pen", kind: "num", render: (r) => r.total_task_penalty },
  ];

  return (
    <div className="container py-3">
      <PageHeader title="Competition Overalls" subtitle={loadedOn(selected?.load_time)} />

      <FilterCard>
        <FilterField label="Competition" className="col-12">
          <AppSelect options={options} onChange={handleChange} placeholder="Select a competition..." />
        </FilterField>
      </FilterCard>

      <DataTable
        columns={columns}
        rows={result}
        rowKey={(r) => r.position}
        rowClassName={(r) => rankClass(r.position, r.competitor_country)}
        empty={selected ? "No results for this competition." : "Select a competition to see the standings."}
      />
    </div>
  );
}
