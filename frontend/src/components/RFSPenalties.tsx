import { useState, useEffect } from "react";
import Select, { SingleValue } from "react-select";
import { api } from "../config/api";

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
                  <th>ID</th>
                  <th>Pilot Name</th>
                  <th>Pilot Country</th>
                  <th>Task Number</th>
                  <th>Task Description</th>
                  <th>Task Penalty</th>
                  <th>Competition Penalty</th>
                  <th>Notes</th>
                </tr>
              </thead>
              <tbody>
                {result.length > 0 &&
                  result.map((user, index) => {
                    const penaltySum = user.task_penalty + user.competition_penalty;
                    return (
                      <tr
                        key={index}
                        className={`${user.competitor_country === "Spain"
                            ? "table-info"
                            : penaltySum === 0
                              ? "table-warning"
                              : "table-danger"
                          }`}
                      >
                        <td>{index + 1}</td>
                        <td>{user.competitor_name}</td>
                        <td>{user.competitor_country}</td>
                        <td>{user.task_number}</td>
                        <td>{user.task_description}</td>
                        <td>{user.task_penalty}</td>
                        <td>{user.competition_penalty}</td>
                        <td>{user.notes}</td>
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
