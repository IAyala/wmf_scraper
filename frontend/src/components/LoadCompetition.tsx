import { useState, useEffect } from "react";
import Select, { SingleValue } from "react-select";
import { api } from "../config/api";

interface IOption {
  value: string;
  label: string;
  load_time: Date;
}

interface ICompetition {
  competition_id: string;
  competition_load_time: string;
  competition_url: string;
  competition_description: string;
}

interface ITaskIncorrect {
  competitor_no_result?: string[];
  result_no_competitor?: string[];
  task_order: number;
}

interface ICompetitionResponse {
  incorrect_tasks_loaded: ITaskIncorrect[];
  status?: string;
}

interface ILoadState {
  is_ok?: boolean;
}

export default function CompetitionOveralls() {
  const [options, setOptions] = useState<IOption[]>();
  const [selected, setSelected] = useState<SingleValue<IOption>>();
  const [result, setResult] = useState<ICompetitionResponse>({
    incorrect_tasks_loaded: [],
  });
  let [reqState, setRequestState] = useState<string>("");
  let [reqOk, setReqOk] = useState<ILoadState>();

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
    setReqOk(undefined);
    setSelected(selected);
  };

  const handleClick = () => {
    function loadCompetitionData() {
      if (selected) {
        let URL = `/load/load_one_competition?competition_id=${selected.value}`;
        api
          .post(URL, {})
          .then((response) => {
            setRequestState("This is good!!");
            setReqOk({ is_ok: true });
            setResult(response.data);
          })
          .catch((error) => {
            setRequestState(error.response.data.detail);
            setReqOk({ is_ok: false });
          });
      }
    }
    loadCompetitionData();
  };

  return (
    <div className="container mt-3">
      <div className="row mt-3">
        <div className="col">
          <Select options={options} onChange={handleChange} />
        </div>
      </div>
      <div className="row mt-3">
        <div className="col">
          <button
            type="button"
            className="btn btn-primary"
            onClick={handleClick}
          >
            Load Competition
          </button>
        </div>
      </div>
      {reqOk === undefined ? ("") : reqOk.is_ok ? (
        result.incorrect_tasks_loaded.length > 0 ? (
          <div className="row mt-3">
            <h5 className="text-warning">
              Request to Load {selected?.label} worked with failures. Status is:{" "}
              {result.status}
            </h5>
            <div className="row mt-3">
              <div className="col">
                <table className="table text-center table-hover shadow">
                  <thead className="table-dark">
                    <tr>
                      <th>Task #</th>
                      <th>Competitor No Result</th>
                      <th>Result no Competitor</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.incorrect_tasks_loaded.map(
                      (result_details: ITaskIncorrect) => {
                        return (
                          <tr key={result_details.task_order}>
                            <td>{result_details.task_order}</td>
                            <td>{result_details.competitor_no_result}</td>
                            <td>{result_details.result_no_competitor}</td>
                          </tr>
                        );
                      }
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        ) : (
          <div className="row mt-3">
            <h5 className="text-success">
              Request to Load {selected?.label} worked. Status is:{" "}
              {result.status}
            </h5>
          </div>
        )
      ) : (
        <h5 className="text-danger">{reqState}</h5>
      )}
    </div>
  );
}
