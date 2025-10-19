import { ReactNode } from "react";
import clsx from "clsx";

type PanelProps = {
  title: string;
  description?: string;
  children?: ReactNode;
  actionLabel?: string;
  onAction?: () => void;
  primary?: boolean;
};

export function Panel({
  title,
  description,
  children,
  actionLabel,
  onAction,
  primary,
}: PanelProps) {
  return (
    <section className={clsx("panel", { primary })}>
      <header>
        <div>
          <h2>{title}</h2>
          {description && <p>{description}</p>}
        </div>
        {actionLabel && onAction && (
          <button type="button" className="ghost" onClick={onAction}>
            {actionLabel}
          </button>
        )}
      </header>
      <div className="panel-body">{children}</div>
    </section>
  );
}
