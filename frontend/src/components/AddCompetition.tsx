import React, { useState } from "react";
import { api } from "../config/api";
import PageHeader from "./PageHeader";

interface ICompetition {
  competition_description: string;
  competition_url: string;
}

interface IState {
  competition: ICompetition;
}

interface ILoadState {
  is_ok?: boolean;
}

interface IProps { }

let AddCompetition: React.FC<IProps> = () => {
  let [state, setState] = useState<IState>({
    competition: {
      competition_description: "",
      competition_url: "",
    },
  });
  let [reqState, setRequestState] = useState<string>("");
  let [reqOk, setReqOk] = useState<ILoadState>();

  let updateInput = (event: React.ChangeEvent<HTMLInputElement>): void => {
    setState({
      competition: {
        ...state.competition,
        [event.target.name]: event.target.value,
      },
    });
  };

  let add_competition = (event: React.FormEvent<HTMLFormElement>): void => {
    event.preventDefault();
    async function writeCompetition() {
      let theGoodURL = state.competition.competition_url.replace(/[&]/g, '%26')
      let URL = `/competition/add_one?competition_description=${state.competition.competition_description}&competition_url=${theGoodURL}`;
      api
        .post(URL, {})
        .then((response) => {
          setRequestState(`Added competition_id: ${response.data.competition_id}`);
          setReqOk({ is_ok: true });
        })
        .catch((error) => {
          setRequestState(error.response.data.detail);
          setReqOk({ is_ok: false });
        });
    }
    writeCompetition();
  };

  return (
    <div className="container py-3">
      <PageHeader
        title="Add Competition"
        subtitle="Register a WatchMeFly event so its results can be loaded."
      />

      <div className="row">
        <div className="col-12 col-lg-8">
          <div className="filter-card">
            <form onSubmit={add_competition}>
              <div className="mb-3">
                <label className="filter-label" htmlFor="competition_description">
                  Description
                </label>
                <input
                  id="competition_description"
                  required={true}
                  name="competition_description"
                  value={state.competition.competition_description}
                  onChange={updateInput}
                  type="text"
                  className="form-control"
                  placeholder="e.g. 2026 French Nationals"
                />
              </div>
              <div className="mb-3">
                <label className="filter-label" htmlFor="competition_url">
                  WatchMeFly URL
                </label>
                <input
                  id="competition_url"
                  required={true}
                  name="competition_url"
                  value={state.competition.competition_url}
                  onChange={updateInput}
                  type="url"
                  className="form-control"
                  placeholder="https://watchmefly.net/events/event.php?e=...&v=tt"
                />
                <div className="form-text">
                  Use the <strong>Results</strong> view of the event, the one ending in <code>&amp;v=tt</code>.
                </div>
              </div>
              <button type="submit" className="btn btn-primary">
                Add Competition
              </button>
            </form>
          </div>

          {reqOk !== undefined && (
            <div className={`alert mt-3 ${reqOk.is_ok ? "alert-success" : "alert-danger"}`} role="alert">
              {reqState}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
export default AddCompetition;
