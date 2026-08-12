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
  competitor_country: string;
  number_competitors: number;
  average_score: number;
  position: number;
}

interface ICompetition {
  competition_id: string;
  competition_load_time: string;
  competition_url: string;
  competition_description: string;
}

export default function CompetitionByCountry() {
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
        const { data } = await api.get(`/query/overall_results_by_country?competition_id=${selected.value}`);
        const results: IResult[] = [];
        data.forEach((value: IResult) => {
          results.push({
            average_score: value.average_score,
            number_competitors: value.number_competitors,
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
    { header: "Country", kind: "text", primary: true, render: (r) => <strong>{r.competitor_country}</strong> },
    { header: "Competitors", kind: "num", render: (r) => r.number_competitors },
    { header: "Average Score", kind: "num", primary: true, render: (r) => <strong>{r.average_score.toLocaleString()}</strong> },
  ];

  return (
    <div className="container py-3">
      <PageHeader title="Country Overalls" subtitle={loadedOn(selected?.load_time)} />

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
        empty={selected ? "No results for this competition." : "Select a competition to see the country ranking."}
      />
    </div>
  );
}
