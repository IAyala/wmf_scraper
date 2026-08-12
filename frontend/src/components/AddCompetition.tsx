import React, { useState } from "react";
import { api } from "../config/api";

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
    <React.Fragment>
      <div className="container mt-3">
        <div className="row mt-3">
          <div className="col-md-8">
            <div className="card">
              <div className="card-header text-center bg-primary text-white">
                <p className="h4">Competition Details</p>
              </div>
              <div className="card-body">
                <form onSubmit={add_competition}>
                  <div className="mb-2">
                    <input
                      required={true}
                      name="competition_description"
                      value={state.competition.competition_description}
                      onChange={updateInput}
                      type="text"
                      className="form-control"
                      placeholder="Description"
                    />
                  </div>
                  <div className="mb-2">
                    <input
                      required={true}
                      name="competition_url"
                      value={state.competition.competition_url}
                      onChange={updateInput}
                      type="text"
                      className="form-control"
                      placeholder="URL"
                    />
                  </div>
                  <div className="mb-2">
                    <input
                      type="submit"
                      className="btn btn-primary"
                      value="Add Competition"
                    />
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
        {reqOk === undefined ? ("") : reqOk.is_ok ? (
          <div className="row mt-3">
            <h5 className="text-success">{reqState}</h5>
          </div>
        ) : (
          <div className="row mt-3">
            <h5 className="text-danger">{reqState}</h5>
          </div>
        )}
      </div>
    </React.Fragment>
  );
};
export default AddCompetition;
