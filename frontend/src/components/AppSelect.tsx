import React from "react";
import Select, { GroupBase, Props } from "react-select";

/**
 * react-select with the menu rendered into document.body.
 *
 * Inline, the menu is trapped by the filter card's stacking context: it gets
 * clipped by `overflow: hidden` and painted under the results table's sticky
 * header. A portal takes it out of both, and the z-index puts it above the
 * sticky navbar (1020) and the status bar (1030).
 */
export default function AppSelect<
  Option,
  IsMulti extends boolean = false,
  Group extends GroupBase<Option> = GroupBase<Option>,
>(props: Props<Option, IsMulti, Group>) {
  return (
    <Select
      {...props}
      menuPortalTarget={typeof document !== "undefined" ? document.body : undefined}
      menuPosition="fixed"
      styles={{
        menuPortal: (base) => ({ ...base, zIndex: 1080 }),
        ...props.styles,
      }}
    />
  );
}
