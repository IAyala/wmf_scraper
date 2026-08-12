import { useState, useEffect } from "react";
import Select, { SingleValue } from "react-select";
import { api } from "../config/api";

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
                  <th>Competitor Name</th>
                  <th>Competitor Country</th>
                  <th>Total Score</th>
                  <th>Average Score</th>
                  <th>Total Comp Penalty</th>
                  <th>Total Task Penalty</th>
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
                        <td>{user.competitor_name}</td>
                        <td>{user.competitor_country}</td>
                        <td>{user.total_score}</td>
                        <td>{user.average_score}</td>
                        <td>{user.total_competition_penalty}</td>
                        <td>{user.total_task_penalty}</td>
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
