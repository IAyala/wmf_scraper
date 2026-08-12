import { useState, useEffect } from "react";
import { SingleValue } from "react-select";
import AppSelect from "./AppSelect";
import { api } from "../config/api";
import DataTable, { IColumn } from "./DataTable";
import FilterCard, { FilterField } from "./FilterCard";
import PageHeader from "./PageHeader";
import { loadedOn } from "./tableHelpers";

interface IOptionCompetition {
  value: string;
  label: string;
  load_time: Date;
}

interface IOptionCountry {
  value: string;
  label: string;
}

interface IOptionCompetitor {
  value: string;
  label: string;
}

interface ICompetition {
  competition_id: string;
  competition_load_time: string;
  competition_url: string;
  competition_description: string;
}

interface ICountry {
  competitor_country: string;
}

interface ICompetitor {
  competitor_name: string;
  competitor_country: string;
}

interface IResult {
  result: string;
  gross_score: number;
  task_penalty: number;
  competition_penalty: number;
  net_score: number;
  task_order: number;
  task_name: string;
  task_status: string;
  notes: string;
}

export default function TasksResultsCompetitor() {
  const [optionsCompetition, setOptionsCompetition] =
    useState<IOptionCompetition[]>();
  const [optionsCountry, setOptionsCountry] = useState<IOptionCountry[]>();
  const [optionsCompetitor, setOptionsCompetitor] =
    useState<IOptionCompetitor[]>();
  const [selectedCompetition, setSelectedCompetition] =
    useState<SingleValue<IOptionCompetition>>();
  const [selectedCompetitor, setSelectedCompetitor] =
    useState<SingleValue<IOptionCompetitor>>();
  const [result, setResult] = useState<IResult[]>([]);

  useEffect(() => {
    async function fetchData() {
      const { data } = await api.get("/competition/get_all_competitions");
      const results: IOptionCompetition[] = [];
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
      setOptionsCompetition(results);
    }
    fetchData();
  }, []);

  const handleChangeCompetition = (
    selected: SingleValue<IOptionCompetition>
  ) => {
    async function fetchCountries(selected: SingleValue<IOptionCompetition>) {
      if (selected) {
        const { data } = await api.get(`/competitor/get_countries_in_competition?competition_id=${selected.value}`);
        const results: IOptionCountry[] = [];
        const sorted_data = data.sort((a: ICountry, b: ICountry) =>
          a.competitor_country.localeCompare(b.competitor_country)
        );
        sorted_data.forEach((value: ICountry) => {
          results.push({
            value: value.competitor_country,
            label: value.competitor_country,
          });
        });
        setOptionsCountry(results);
      }
    }
    setSelectedCompetition(selected);
    fetchCountries(selected);
  };

  const handleChangeCountry = (selected: SingleValue<IOptionCountry>) => {
    async function fetchCompetitors(selected: SingleValue<IOptionCountry>) {
      if (selected && selectedCompetition) {
        const { data } = await api.get(`/competitor/get_competitors_in_competition_by_country?competition_id=${selectedCompetition.value}&country_name=${selected.value}`);
        const results: IOptionCompetitor[] = [];

        data.forEach((value: ICompetitor) => {
          results.push({
            value: value.competitor_name,
            label: value.competitor_name,
          });
        });
        setOptionsCompetitor(results);
      }
    }
    fetchCompetitors(selected);
  };

  const handleChangeCompetitor = (selected: SingleValue<IOptionCompetitor>) => {
    async function fetchResults(selected: SingleValue<IOptionCompetitor>) {
      if (selected && selectedCompetition) {
        const { data } = await api.get(`/query/results_competitor_in_competition?competition_id=${selectedCompetition.value}&competitor_name=${selected.value}`);
        const results: IResult[] = [];
        data.forEach((value: IResult) => {
          results.push({
            result: value.result,
            gross_score: value.gross_score,
            task_penalty: value.task_penalty,
            competition_penalty: value.competition_penalty,
            net_score: value.net_score,
            task_order: value.task_order,
            task_name: value.task_name,
            task_status: value.task_status,
            notes: value.notes,
          });
        });
        setResult(results);
      }
    }
    setSelectedCompetitor(selected);
    fetchResults(selected);
  };

  const columns: IColumn<IResult>[] = [
    { header: "Task", kind: "num", primary: true, render: (r) => <span className="rank-badge">{r.task_order}</span> },
    { header: "Name", kind: "text", primary: true, render: (r) => <strong>{r.task_name}</strong> },
    { header: "Status", kind: "text", render: (r) => <span className="badge bg-secondary">{r.task_status}</span> },
    { header: "Result", kind: "num", render: (r) => r.result },
    { header: "Gross", kind: "num", render: (r) => r.gross_score.toLocaleString() },
    { header: "Comp Pen", kind: "num", render: (r) => r.competition_penalty || "—" },
    { header: "Task Pen", kind: "num", render: (r) => r.task_penalty || "—" },
    { header: "Net", kind: "num", primary: true, render: (r) => <strong>{r.net_score.toLocaleString()}</strong> },
    { header: "Notes", kind: "notes", render: (r) => r.notes },
  ];

  const subtitle = [loadedOn(selectedCompetition?.load_time), selectedCompetitor?.label]
    .filter(Boolean)
    .join(" · ");

  return (
    <div className="container py-3">
      <PageHeader title="Results by Competitor" subtitle={subtitle || undefined} />

      <FilterCard>
        <FilterField label="Competition" className="col-12 col-lg-4">
          <AppSelect
            options={optionsCompetition}
            onChange={handleChangeCompetition}
            placeholder="Select a competition..."
          />
        </FilterField>
        <FilterField label="Country" className="col-12 col-md-6 col-lg-4">
          <AppSelect
            options={optionsCountry}
            onChange={handleChangeCountry}
            isDisabled={!optionsCountry}
            placeholder={optionsCountry ? "Select a country..." : "Pick a competition first"}
          />
        </FilterField>
        <FilterField label="Competitor" className="col-12 col-md-6 col-lg-4">
          <AppSelect
            options={optionsCompetitor}
            onChange={handleChangeCompetitor}
            isDisabled={!optionsCompetitor}
            placeholder={optionsCompetitor ? "Select a competitor..." : "Pick a country first"}
          />
        </FilterField>
      </FilterCard>

      <DataTable
        columns={columns}
        rows={result}
        rowKey={(r) => r.task_order}
        rowClassName={(r) => (r.task_penalty > 0 || r.competition_penalty > 0 ? "table-danger" : undefined)}
        empty={
          selectedCompetitor
            ? "No results for this competitor."
            : "Choose a competition, a country and a competitor."
        }
      />
    </div>
  );
}
