import { useEffect, useState } from "react";
import { fetchVersion } from "../config/api";

/** The version reported by the server, or undefined until it answers. */
export const useVersion = (): string | undefined => {
  const [version, setVersion] = useState<string>();

  useEffect(() => {
    let active = true;
    fetchVersion()
      .then((value) => {
        if (active) setVersion(value);
      })
      .catch(() => undefined);
    return () => {
      active = false;
    };
  }, []);

  return version;
};
