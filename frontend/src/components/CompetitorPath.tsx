import { useState, useEffect, useRef } from "react";
import Select, { SingleValue, MultiValue } from "react-select";
import { api } from "../config/api";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
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

  const [divWidth, setDivWidth] = useState(0); // Initialize the width as 0
  const myDivRef = useRef<HTMLDivElement | null>(null);

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

    const updateDivWidth = () => {
      if (myDivRef.current) {
        const newWidth = myDivRef.current.clientWidth;
        setDivWidth(newWidth);
      }
    };

    fetchData();
    updateDivWidth();

    // Add event listener for window resize
    window.addEventListener("resize", updateDivWidth);

    // Clean up the event listener on component unmount
    return () => {
      window.removeEventListener("resize", updateDivWidth);
    };
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

  return (
    <div className="container mt-3">
      <div className="row mt-3">
        <div className="col" ref={myDivRef}>
          <Select
            options={optionsCompetition}
            onChange={handleChangeCompetition}
          />
        </div>
      </div>
      <div className="row mt-3">
        <div className="col">
          <Select
            isMulti
            value={selectedCompetitor}
            options={optionsCompetitor}
            onChange={handleChangeCompetitor}
          />
        </div>
      </div>
      <div className="row mt-3">
        {selectedCompetition && selectedCompetitor && (
          <h5>
            Competition loaded on{" "}
            {selectedCompetition?.load_time.toString().slice(0, 24)}
          </h5>
        )}
      </div>
      {result && optionsCompetitor && (
        <div className="row mt-3">
          <div className="col">
            <div
              className="container"
              style={{ width: "100%", height: "400px" }}
            >
              {result.data.length > 0 && (
                <LineChart
                  width={divWidth - 40}
                  height={Math.max(10 * optionsCompetitor.length, 400)}
                  data={result.data}
                >
                  <CartesianGrid strokeDasharray="5 5" />
                  <XAxis dataKey="x" />
                  <YAxis
                    ticks={Array.from(
                      { length: optionsCompetitor.length },
                      (_, i) => i + 1
                    )}
                    reversed={true}
                  />
                  <Tooltip />
                  <Legend />
                  {Object.keys(result.data[0])
                    .filter((element) => element !== "x")
                    .map((the_key, index) => {
                      return (
                        <Line
                          type="monotone"
                          dataKey={the_key}
                          stroke={colours[index]}
                          activeDot={{ r: 6 }}
                          name={the_key}
                        />
                      );
                    })}
                </LineChart>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
