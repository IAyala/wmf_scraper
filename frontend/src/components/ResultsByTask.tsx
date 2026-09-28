import { useState, useEffect } from "react";
import { SingleValue } from "react-select";
import AppSelect from "./AppSelect";
import { api } from "../config/api";
import DataTable, { IColumn } from "./DataTable";
import FilterCard, { FilterField } from "./FilterCard";
import PageHeader from "./PageHeader";
import { IFlightStamp, flightLabel, loadedOn, rankClass } from "./tableHelpers";

interface IOptionCompetition {
  value: string;
  label: string;
  load_time: Date;
}

interface IOptionTask {
  value: number;
  label: string;
  task: ITask;
}

interface ICompetition {
  competition_id: string;
  competition_load_time: string;
  competition_url: string;
  competition_description: string;
}

interface ITask extends IFlightStamp {
  task_order: number;
  task_name: string;
  task_status: string;
}

interface IResult {
  position: number;
  competitor_name: string;
  competitor_country: string;
  result: string;
  gross_score: number;
  task_penalty: number;
  competition_penalty: number;
  net_score: number;
  notes: string;
}

export default function ResultsByTask() {
  const [optionsCompetition, setOptionsCompetition] = useState<IOptionCompetition[]>();
  const [optionsTask, setOptionsTask] = useState<IOptionTask[]>();
  const [selectedCompetition, setSelectedCompetition] = useState<SingleValue<IOptionCompetition>>();
  const [selectedTask, setSelectedTask] = useState<SingleValue<IOptionTask>>();
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
    async function fetchTasks(selected: SingleValue<IOptionCompetition>) {
      if (selected) {
        const { data } = await api.get(`/query/tasks_in_competition?competition_id=${selected.value}`);
        setOptionsTask(
          data.map((task: ITask) => ({
            value: task.task_order,
            label: `Task ${task.task_order} · ${task.task_name}`,
            task,
          }))
        );
      }
    }
    setSelectedCompetition(selected);
    setSelectedTask(null);
    setResult([]);
    fetchTasks(selected);
  };

  const handleChangeTask = (selected: SingleValue<IOptionTask>) => {
    async function fetchResults(selected: SingleValue<IOptionTask>) {
      if (selected && selectedCompetition) {
        const { data } = await api.get(
          `/query/task_results_competition?competition_id=${selectedCompetition.value}&task_order=${selected.value}`
        );
        setResult(data);
      }
    }
    setSelectedTask(selected);
    fetchResults(selected);
  };

  const columns: IColumn<IResult>[] = [
    { header: "Pos", kind: "num", primary: true, render: (r) => <span className="rank-badge">{r.position}</span> },
    { header: "Competitor", kind: "text", primary: true, render: (r) => <strong>{r.competitor_name}</strong> },
    { header: "Country", kind: "text", render: (r) => r.competitor_country },
    { header: "Result", kind: "num", render: (r) => r.result },
    { header: "Gross", kind: "num", render: (r) => r.gross_score.toLocaleString() },
    { header: "Comp Pen", kind: "num", render: (r) => r.competition_penalty || "—" },
    { header: "Task Pen", kind: "num", render: (r) => r.task_penalty || "—" },
    { header: "Net", kind: "num", primary: true, render: (r) => <strong>{r.net_score.toLocaleString()}</strong> },
    { header: "Notes", kind: "notes", render: (r) => r.notes },
  ];

  const task = selectedTask?.task;
  const subtitle = [
    loadedOn(selectedCompetition?.load_time),
    task?.task_status,
    task && task.flight_number !== null ? flightLabel(task) : undefined,
  ]
    .filter(Boolean)
    .join(" · ");

  return (
    <div className="container py-3">
      <PageHeader title="Results by Task" subtitle={subtitle || undefined} />

      <FilterCard>
        <FilterField label="Competition" className="col-12 col-lg-6">
          <AppSelect
            options={optionsCompetition}
            onChange={handleChangeCompetition}
            placeholder="Select a competition..."
          />
        </FilterField>
        <FilterField label="Task" className="col-12 col-lg-6">
          <AppSelect
            value={selectedTask}
            options={optionsTask}
            onChange={handleChangeTask}
            isDisabled={!optionsTask?.length}
            placeholder={
              optionsTask?.length
                ? "Select a task..."
                : optionsTask
                  ? "No tasks stored for this competition"
                  : "Pick a competition first"
            }
          />
        </FilterField>
      </FilterCard>

      <DataTable
        columns={columns}
        rows={result}
        rowKey={(r) => r.competitor_name}
        rowClassName={(r) => rankClass(r.position, r.competitor_country)}
        empty={
          selectedTask ? "No results stored for this task." : "Select a competition and a task to see how it scored."
        }
      />
    </div>
  );
}
