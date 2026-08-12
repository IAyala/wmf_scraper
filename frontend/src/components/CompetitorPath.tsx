import { useState, useEffect } from "react";
import { SingleValue, MultiValue } from "react-select";
import AppSelect from "./AppSelect";
import { api } from "../config/api";
import FilterCard, { FilterField } from "./FilterCard";
import PageHeader from "./PageHeader";
import { loadedOn } from "./tableHelpers";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

interface IOptionCompetition {
  value: string;
  label: string;
  load_time: Date;
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

interface ICompetitor {
  competitor_name: string;
  competitor_country: string;
}

interface IValues {
  [key: string]: number[] | string[];
}

interface IValue {
  [key: string]: number | string;
}

interface IResult {
  data: IValue[];
}

export default function CompetitorPath() {
  const colours: string[] = [
    "#0d0c26",
    "#d78884",
    "#848B00",
    "#84d3d7",
    "#2b0272",
    "#ec040b",
  ];
  const [optionsCompetition, setOptionsCompetition] =
    useState<IOptionCompetition[]>();
  const [optionsCompetitor, setOptionsCompetitor] =
    useState<IOptionCompetitor[]>();
  const [selectedCompetition, setSelectedCompetition] =
    useState<SingleValue<IOptionCompetition>>();
  const [selectedCompetitor, setSelectedCompetitor] =
    useState<MultiValue<IOptionCompetitor>>();
  const [result, setResult] = useState<IResult>();

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
    async function fetchCompetitors(selected: SingleValue<IOptionCompetition>) {
      if (selected) {
        const { data } = await api.get(`/competitor/get_competitors_in_competition?competition_id=${selected.value}`);
        const results: IOptionCompetitor[] = [];
        const sorted_data = data.sort((a: ICompetitor, b: ICompetitor) =>
          a.competitor_name.localeCompare(b.competitor_name)
        );
        sorted_data.forEach((value: ICompetitor) => {
          results.push({
            value: value.competitor_name,
            label: value.competitor_name,
          });
        });
        setOptionsCompetitor(results);
      }
    }
    setSelectedCompetition(selected);
    setSelectedCompetitor([]);
    fetchCompetitors(selected);
  };

  const handleChangeCompetitor = (selected: MultiValue<IOptionCompetitor>) => {
    async function fetchResults(selected: MultiValue<IOptionCompetitor>) {
      if (selected && selectedCompetition && selected.length > 0) {
        console.log(selected)
        let the_values: IValues = {};

        for (const selectedCompetitor of selected) {
          const { data } = await api.get(`/query/position_path_in_competition?competition_id=${selectedCompetition.value}&competitor_name=${selectedCompetitor.value}`);
          the_values[selectedCompetitor.label] = data.competitor_positions;
          if (!("x" in the_values)) {
            the_values["x"] = Array.from({
              length: data.competitor_positions.length,
            }).map((_, i) => `Task ${i + 1}`);
          }
        }

        const result: IValue[] = the_values["x"].map((_, i) => {
          const newItem: IValue = {};
          for (const key of Object.keys(the_values)) {
            newItem[key] = the_values[key][i];
          }
          return newItem;
        });

        const to_set: IResult = {
          data: result,
        };

        setResult(to_set);
      }
    }
    setSelectedCompetitor(selected);
    fetchResults(selected);
  };

  const competitorCount = selectedCompetitor?.length ?? 0;
  const chartHeight = Math.min(720, Math.max(340, 60 + competitorCount * 26));

  // Positions run 1..N. Pin the axis to that range with a handful of round
  // ticks; left to itself, a reversed axis picks a confusing set.
  const positions = (result?.data ?? []).flatMap((row) =>
    Object.entries(row)
      .filter(([key]) => key !== "x")
      .map(([, value]) => Number(value))
      .filter((value) => Number.isFinite(value) && value > 0)
  );
  const maxPosition = positions.length > 0 ? Math.max(...positions) : 10;
  const tickStep = Math.max(1, Math.ceil(maxPosition / 6));
  const positionTicks = [1];
  for (let tick = tickStep; tick <= maxPosition; tick += tickStep) {
    if (tick > 1) positionTicks.push(tick);
  }
  if (positionTicks[positionTicks.length - 1] !== maxPosition) positionTicks.push(maxPosition);

  return (
    <div className="container py-3">
      <PageHeader
        title="Competitor Results Path"
        subtitle={loadedOn(selectedCompetition?.load_time)}
      />

      <FilterCard>
        <FilterField label="Competition" className="col-12 col-lg-5">
          <AppSelect
            options={optionsCompetition}
            onChange={handleChangeCompetition}
            placeholder="Select a competition..."
          />
        </FilterField>
        <FilterField label="Competitors" className="col-12 col-lg-7">
          <AppSelect
            isMulti
            value={selectedCompetitor}
            options={optionsCompetitor}
            onChange={handleChangeCompetitor}
            isDisabled={!optionsCompetitor}
            placeholder={optionsCompetitor ? "Add one or more competitors..." : "Pick a competition first"}
          />
        </FilterField>
      </FilterCard>

      {result && result.data.length > 0 ? (
        <div className="table-card p-2 p-md-3">
          <p className="page-subtitle mb-2">Position after each task — lower is better.</p>
          {/* ResponsiveContainer keeps the chart inside the card at any width,
              which a measured pixel width never managed to do on a phone. */}
          <ResponsiveContainer width="100%" height={chartHeight}>
            <LineChart data={result.data} margin={{ top: 8, right: 12, bottom: 4, left: 0 }}>
              <CartesianGrid strokeDasharray="5 5" />
              <XAxis dataKey="x" tick={{ fontSize: 12 }} />
              <YAxis
                type="number"
                domain={[1, maxPosition]}
                ticks={positionTicks}
                interval={0}
                allowDecimals={false}
                reversed={true}
                tick={{ fontSize: 12 }}
                width={34}
              />
              <Tooltip />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              {Object.keys(result.data[0])
                .filter((element) => element !== "x")
                .map((the_key, index) => (
                  <Line
                    key={the_key}
                    type="monotone"
                    dataKey={the_key}
                    stroke={colours[index % colours.length]}
                    strokeWidth={2}
                    dot={{ r: 3 }}
                    activeDot={{ r: 6 }}
                    name={the_key}
                  />
                ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="empty-state">
          {selectedCompetition
            ? "Pick one or more competitors to plot their position through the tasks."
            : "Select a competition to start."}
        </div>
      )}
    </div>
  );
}
