import { useState, useEffect } from "react";
import { SingleValue } from "react-select";
import AppSelect from "./AppSelect";
import { api } from "../config/api";
import DataTable, { IColumn } from "./DataTable";
import FilterCard, { FilterField } from "./FilterCard";
import PageHeader from "./PageHeader";

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

  const incorrectColumns: IColumn<ITaskIncorrect>[] = [
    { header: "Task", kind: "num", primary: true, render: (t) => <span className="rank-badge">{t.task_order}</span> },
    {
      header: "Competitor without result",
      kind: "text",
      render: (t) => (t.competitor_no_result?.length ? t.competitor_no_result.join(", ") : "—"),
    },
    {
      header: "Result without competitor",
      kind: "text",
      render: (t) => (t.result_no_competitor?.length ? t.result_no_competitor.join(", ") : "—"),
    },
  ];

  return (
    <div className="container py-3">
      <PageHeader
        title="Load Competition"
        subtitle="Re-scrapes WatchMeFly and replaces this competition's stored results."
      />

      <FilterCard>
        <FilterField label="Competition" className="col-12 col-md-8">
          <AppSelect options={options} onChange={handleChange} placeholder="Select a competition..." />
        </FilterField>
        <div className="col-12 col-md-4 d-flex align-items-end">
          <button type="button" className="btn btn-primary w-100" onClick={handleClick} disabled={!selected}>
            Load Competition
          </button>
        </div>
      </FilterCard>

      {reqOk === undefined ? null : reqOk.is_ok ? (
        result.incorrect_tasks_loaded.length > 0 ? (
          <>
            <div className="alert alert-warning" role="alert">
              <strong>{selected?.label}</strong> loaded with warnings. Status: {result.status}
            </div>
            <DataTable
              columns={incorrectColumns}
              rows={result.incorrect_tasks_loaded}
              rowKey={(t) => t.task_order}
              empty="No task discrepancies."
            />
          </>
        ) : (
          <div className="alert alert-success" role="alert">
            <strong>{selected?.label}</strong> loaded. Status: {result.status}
          </div>
        )
      ) : (
        <div className="alert alert-danger" role="alert">
          {reqState}
        </div>
      )}
    </div>
  );
}
