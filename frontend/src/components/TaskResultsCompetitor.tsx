import { useState, useEffect } from "react";
import Select, { SingleValue } from "react-select";
import { api } from "../config/api";

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

  return (
    <div className="container mt-3">
      <div className="row mt-3">
        <div className="col">
          <Select
            options={optionsCompetition}
            onChange={handleChangeCompetition}
          />
        </div>
      </div>
      <div className="row mt-3">
        <div className="col">
          <Select options={optionsCountry} onChange={handleChangeCountry} />
        </div>
      </div>
      <div className="row mt-3">
        <div className="col">
          <Select
            options={optionsCompetitor}
            onChange={handleChangeCompetitor}
          />
        </div>
      </div>
      <div className="row mt-3">
        {selectedCompetition && selectedCompetitor && (
          <h5>
            Competition loaded on{" "}
            {selectedCompetition?.load_time.toString().slice(0, 24)} Results for
            competitor: {selectedCompetitor.label}
          </h5>
        )}
      </div>
      <div className="row mt-3">
        {result.length > 0 && (
          <div className="col">
            <table className="table text-center table-hover shadow">
              <thead className="table-dark">
                <tr>
                  <th>Task #</th>
                  <th>Name</th>
                  <th>Status</th>
                  <th>Result</th>
                  <th>Gross Score</th>
                  <th>Comp Penalty</th>
                  <th>Task Penalty</th>
                  <th>Net Score</th>
                  <th>Notes</th>
                </tr>
              </thead>
              <tbody>
                {result.length > 0 &&
                  result.map((result_details) => {
                    return (
                      <tr
                        key={result_details.task_order}
                        className={`${result_details.task_penalty > 0 ||
                            result_details.competition_penalty > 0
                            ? "table-danger"
                            : ""
                          }`}
                      >
                        <td>{result_details.task_order}</td>
                        <td>{result_details.task_name}</td>
                        <td>{result_details.task_status}</td>
                        <td>{result_details.result}</td>
                        <td>{result_details.gross_score}</td>
                        <td>{result_details.competition_penalty}</td>
                        <td>{result_details.task_penalty}</td>
                        <td>{result_details.net_score}</td>
                        <td>{result_details.notes}</td>
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
