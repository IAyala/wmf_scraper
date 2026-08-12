import { useState, useEffect } from "react";
import Select, { SingleValue } from "react-select";
import { api } from "../config/api";

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

  return (
    <div className="container mt-3">
      <div className="row mt-3">
        <div className="col">
          <Select options={options} onChange={handleChange} />
        </div>
      </div>
      <div className="row mt-3">
        {selected && (
          <h5>
            Competition loaded on {selected?.load_time.toString().slice(0, 24)}
          </h5>
        )}
      </div>
      <div className="row mt-3">
        {result.length > 0 && (
          <div className="col">
            <table className="table text-center table-hover shadow">
              <thead className="table-dark">
                <tr>
                  <th>Position</th>
                  <th>Competitor Country</th>
                  <th>Number Competitors</th>
                  <th>Average Score</th>
                </tr>
              </thead>
              <tbody>
                {result.length > 0 &&
                  result.map((user) => {
                    return (
                      <tr
                        key={user.position}
                        className={`${user.competitor_country === "Spain"
                            ? "table-warning"
                            : ""
                          }`}
                      >
                        <td>{user.position}</td>
                        <td>{user.competitor_country}</td>
                        <td>{user.number_competitors}</td>
                        <td>{user.average_score}</td>
                      </tr>
                    );
                  })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
