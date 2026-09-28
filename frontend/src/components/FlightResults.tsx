import { useState, useEffect } from "react";
import { SingleValue } from "react-select";
import AppSelect from "./AppSelect";
import { api } from "../config/api";
import DataTable, { IColumn } from "./DataTable";
import FilterCard, { FilterField } from "./FilterCard";
import PageHeader from "./PageHeader";
import { IFlight, flightLabel, loadedOn, rankClass } from "./tableHelpers";

interface IOptionCompetition {
  value: string;
  label: string;
  load_time: Date;
}

interface IOptionFlight {
  value: number;
  label: string;
  tasks: number[];
}

interface ICompetition {
  competition_id: string;
  competition_load_time: string;
  competition_url: string;
  competition_description: string;
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

export default function FlightResults() {
  const [optionsCompetition, setOptionsCompetition] = useState<IOptionCompetition[]>();
  const [optionsFlight, setOptionsFlight] = useState<IOptionFlight[]>();
  const [selectedCompetition, setSelectedCompetition] = useState<SingleValue<IOptionCompetition>>();
  const [selectedFlight, setSelectedFlight] = useState<SingleValue<IOptionFlight>>();
  const [result, setResult] = useState<IResult[]>([]);

  useEffect(() => {
    async function fetchData() {
      const { data } = await api.get("/competition/get_all_competitions");
      const results: IOptionCompetition[] = [];
      const sorted_data = data.sort(
        (a: ICompetition, b: ICompetition) =>
          new Date(b.competition_load_time).getTime() - new Date(a.competition_load_time).getTime()
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

  const handleChangeCompetition = (selected: SingleValue<IOptionCompetition>) => {
    async function fetchFlights(selected: SingleValue<IOptionCompetition>) {
      if (selected) {
        const { data } = await api.get(`/query/flights_in_competition?competition_id=${selected.value}`);
        setOptionsFlight(
          data.map((flight: IFlight) => ({
            value: flight.flight_number,
            label: flightLabel(flight),
            tasks: flight.task_orders,
          }))
        );
      }
    }
    setSelectedCompetition(selected);
    setSelectedFlight(null);
    setResult([]);
    fetchFlights(selected);
  };

  const handleChangeFlight = (selected: SingleValue<IOptionFlight>) => {
    async function fetchResults(selected: SingleValue<IOptionFlight>) {
      if (selected && selectedCompetition) {
        const { data } = await api.get(
          `/query/flight_results_competition?competition_id=${selectedCompetition.value}&flight_number=${selected.value}`
        );
        setResult(data);
      }
    }
    setSelectedFlight(selected);
    fetchResults(selected);
  };

  const columns: IColumn<IResult>[] = [
    { header: "Pos", kind: "num", primary: true, render: (r) => <span className="rank-badge">{r.position}</span> },
    { header: "Competitor", kind: "text", primary: true, render: (r) => <strong>{r.competitor_name}</strong> },
    { header: "Country", kind: "text", render: (r) => r.competitor_country },
    { header: "Flight Total", kind: "num", primary: true, render: (r) => <strong>{r.total_score.toLocaleString()}</strong> },
    { header: "Average", kind: "num", render: (r) => r.average_score.toLocaleString() },
    { header: "Comp Pen", kind: "num", render: (r) => r.total_competition_penalty || "—" },
    { header: "Task Pen", kind: "num", render: (r) => r.total_task_penalty || "—" },
  ];

  const tasksFlown = selectedFlight?.tasks.length
    ? `Tasks ${selectedFlight.tasks.join(", ")}`
    : undefined;
  const subtitle = [loadedOn(selectedCompetition?.load_time), tasksFlown].filter(Boolean).join(" · ");

  return (
    <div className="container py-3">
      <PageHeader title="Results by Flight" subtitle={subtitle || undefined} />

      <FilterCard>
        <FilterField label="Competition" className="col-12 col-lg-7">
          <AppSelect
            options={optionsCompetition}
            onChange={handleChangeCompetition}
            placeholder="Select a competition..."
          />
        </FilterField>
        <FilterField label="Flight" className="col-12 col-lg-5">
          <AppSelect
            value={selectedFlight}
            options={optionsFlight}
            onChange={handleChangeFlight}
            isDisabled={!optionsFlight?.length}
            placeholder={
              optionsFlight?.length
                ? "Select a flight..."
                : optionsFlight
                  ? "No flights for this competition"
                  : "Pick a competition first"
            }
          />
        </FilterField>
      </FilterCard>

      <DataTable
        columns={columns}
        rows={result}
        rowKey={(r) => r.position}
        rowClassName={(r) => rankClass(r.position, r.competitor_country)}
        empty={
          selectedFlight
            ? "No results for this flight."
            : "Select a competition and a flight to see how that morning went."
        }
      />
    </div>
  );
}
