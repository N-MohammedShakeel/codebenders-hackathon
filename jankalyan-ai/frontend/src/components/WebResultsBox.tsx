import React, { useEffect, useState } from "react";
import { fetchWebResults, TavilySearchResponse } from "../lib/api";

interface WebResultsBoxProps {
  state: string;
  enabled: boolean;
}

export const WebResultsBox: React.FC<WebResultsBoxProps> = ({ state, enabled }) => {
  const [data, setData] = useState<TavilySearchResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    if (!enabled || !state) return;
    let cancelled = false;
    setLoading(true);
    fetchWebResults(`${state} government welfare schemes official`).then((res) => {
      if (cancelled) return;
      setData(res);
      setLoading(false);
    });
    return () => {
      cancelled = true;
    };
  }, [enabled, state]);

  if (!enabled) return null;

  return (
    <div className="bg-white rounded-2xl shadow-md border border-slate-200 p-5">
      <h3 className="text-sm font-bold text-slate-900 mb-3">Latest official web results</h3>

      {loading && <p className="text-xs text-slate-500">Searching official sources…</p>}

      {!loading && data && (
        <>
          {data.results.length === 0 ? (
            <p className="text-xs text-slate-600">No live results. Check the official portals listed on each scheme.</p>
          ) : (
            <ul className="space-y-3">
              {data.results.map((r, idx) => (
                <li key={`${r.url ?? "result"}-${idx}`} className="border-t border-slate-100 pt-3 first:border-t-0 first:pt-0">
                  <p className="text-sm font-semibold text-slate-900">{r.title || r.url}</p>
                  {r.url && (
                    <a
                      href={r.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-emerald-700 hover:underline break-all"
                    >
                      {r.url}
                    </a>
                  )}
                  {(r.snippet || r.content) && (
                    <p className="text-xs text-slate-600 mt-1">{r.snippet || r.content}</p>
                  )}
                </li>
              ))}
            </ul>
          )}

          {data.isMock && <p className="text-[11px] text-slate-400 mt-3">{data.note}</p>}
          {data.verifiedAt && (
            <p className="text-[11px] text-slate-400 mt-1">Time checked: {data.verifiedAt}</p>
          )}
        </>
      )}
    </div>
  );
};

export default WebResultsBox;
