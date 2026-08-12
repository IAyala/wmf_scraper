import React, { useCallback, useEffect, useState } from "react";
import axios from "axios";
import { api } from "../config/api";
import DataTable, { IColumn } from "./DataTable";
import PageHeader from "./PageHeader";

interface ICompetition {
  competition_id: number;
  competition_description: string;
  competition_url: string;
  competition_load_time: string;
}

interface IFeedback {
  ok: boolean;
  message: string;
}

const errorMessage = (error: unknown, fallback: string): string => {
  if (axios.isAxiosError(error)) {
    return error.response?.data?.detail ?? error.message ?? fallback;
  }
  return fallback;
};

export default function EditCompetitions() {
  const [competitions, setCompetitions] = useState<ICompetition[]>([]);
  const [editing, setEditing] = useState<ICompetition | null>(null);
  const [deleting, setDeleting] = useState<ICompetition | null>(null);
  const [draft, setDraft] = useState({ competition_description: "", competition_url: "" });
  const [busy, setBusy] = useState(false);
  const [feedback, setFeedback] = useState<IFeedback>();

  const refresh = useCallback(async () => {
    const { data } = await api.get<ICompetition[]>("/competition/get_all_competitions");
    setCompetitions(
      [...data].sort((a, b) => a.competition_description.localeCompare(b.competition_description))
    );
  }, []);

  useEffect(() => {
    refresh().catch((error) => setFeedback({ ok: false, message: errorMessage(error, "Could not load competitions") }));
  }, [refresh]);

  const startEdit = (competition: ICompetition) => {
    setDeleting(null);
    setFeedback(undefined);
    setEditing(competition);
    setDraft({
      competition_description: competition.competition_description,
      competition_url: competition.competition_url,
    });
  };

  const startDelete = (competition: ICompetition) => {
    setEditing(null);
    setFeedback(undefined);
    setDeleting(competition);
  };

  const cancel = () => {
    setEditing(null);
    setDeleting(null);
  };

  const save = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!editing) return;
    setBusy(true);
    try {
      await api.post(`/competition/update_one?competition_id=${editing.competition_id}`, draft);
      await refresh();
      setEditing(null);
      setFeedback({ ok: true, message: `Updated "${draft.competition_description}".` });
    } catch (error) {
      setFeedback({ ok: false, message: errorMessage(error, "Could not update the competition") });
    } finally {
      setBusy(false);
    }
  };

  const confirmDelete = async () => {
    if (!deleting) return;
    setBusy(true);
    try {
      const { data } = await api.post(`/competition/remove_one?competition_id=${deleting.competition_id}`);
      await refresh();
      setFeedback({
        ok: true,
        message:
          `Removed "${deleting.competition_description}", along with ` +
          `${data.number_tasks_removed} task(s) and ${data.number_task_results_removed} result(s).`,
      });
      setDeleting(null);
    } catch (error) {
      setFeedback({ ok: false, message: errorMessage(error, "Could not remove the competition") });
    } finally {
      setBusy(false);
    }
  };

  const columns: IColumn<ICompetition>[] = [
    {
      header: "Competition",
      kind: "text",
      primary: true,
      render: (c) => <strong>{c.competition_description}</strong>,
    },
    {
      header: "URL",
      kind: "text",
      render: (c) => (
        <a href={c.competition_url} target="_blank" rel="noreferrer" className="small">
          {c.competition_url}
        </a>
      ),
    },
    {
      header: "Loaded",
      kind: "text",
      render: (c) =>
        c.competition_load_time
          ? new Date(c.competition_load_time).toLocaleString(undefined, {
              dateStyle: "medium",
              timeStyle: "short",
            })
          : "never",
    },
    {
      header: "Actions",
      kind: "num",
      primary: true,
      render: (c) => (
        <span className="d-inline-flex gap-2">
          <button type="button" className="btn btn-outline-primary btn-sm" onClick={() => startEdit(c)}>
            Edit
          </button>
          <button type="button" className="btn btn-outline-danger btn-sm" onClick={() => startDelete(c)}>
            Delete
          </button>
        </span>
      ),
    },
  ];

  return (
    <div className="container py-3">
      <PageHeader
        title="Edit Competitions"
        subtitle="Rename a competition, correct its URL, or remove it entirely."
      />

      {feedback && (
        <div className={`alert ${feedback.ok ? "alert-success" : "alert-danger"}`} role="alert">
          {feedback.message}
        </div>
      )}

      {editing && (
        <div className="filter-card mb-3">
          <form onSubmit={save}>
            <div className="row g-3">
              <div className="col-12 col-lg-5">
                <label className="filter-label" htmlFor="edit_description">
                  Description
                </label>
                <input
                  id="edit_description"
                  className="form-control"
                  required
                  value={draft.competition_description}
                  onChange={(e) => setDraft({ ...draft, competition_description: e.target.value })}
                />
              </div>
              <div className="col-12 col-lg-7">
                <label className="filter-label" htmlFor="edit_url">
                  WatchMeFly URL
                </label>
                <input
                  id="edit_url"
                  className="form-control"
                  type="url"
                  required
                  value={draft.competition_url}
                  onChange={(e) => setDraft({ ...draft, competition_url: e.target.value })}
                />
              </div>
            </div>
            <div className="form-text mt-2">
              Editing the URL does not re-read WatchMeFly. Run <strong>Load Competition</strong> afterwards to
              refresh the stored tasks and results.
            </div>
            <div className="d-flex gap-2 mt-3">
              <button type="submit" className="btn btn-primary" disabled={busy}>
                {busy ? "Saving..." : "Save changes"}
              </button>
              <button type="button" className="btn btn-outline-secondary" onClick={cancel} disabled={busy}>
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {deleting && (
        <div className="alert alert-danger" role="alert">
          <p className="mb-2">
            Remove <strong>{deleting.competition_description}</strong>? This also deletes every task and result
            stored for it. It cannot be undone.
          </p>
          <div className="d-flex gap-2">
            <button type="button" className="btn btn-danger" onClick={confirmDelete} disabled={busy}>
              {busy ? "Removing..." : "Yes, remove it"}
            </button>
            <button type="button" className="btn btn-outline-secondary" onClick={cancel} disabled={busy}>
              Cancel
            </button>
          </div>
        </div>
      )}

      <DataTable
        columns={columns}
        rows={competitions}
        rowKey={(c) => c.competition_id}
        rowClassName={(c) => (c.competition_id === editing?.competition_id ? "table-primary" : undefined)}
        empty="No competitions yet. Add one from the Manage menu."
      />
    </div>
  );
}
