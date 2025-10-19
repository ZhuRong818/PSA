type Filters = {
  skill: string;
  difficulty: string;
  min_hours: string;
  max_hours: string;
};

type Props = {
  filters: Filters;
  onChange: (filters: Filters) => void;
};

const difficultyOptions = [
  { value: "", label: "Any level" },
  { value: "Beginner", label: "Beginner" },
  { value: "Intermediate", label: "Intermediate" },
  { value: "Advanced", label: "Advanced" },
];

export function CourseFilters({ filters, onChange }: Props) {
  return (
    <div className="filters">
      <div>
        <label>Skill</label>
        <input
          type="text"
          placeholder="Cloud Architecture"
          value={filters.skill}
          onChange={(evt) => onChange({ ...filters, skill: evt.target.value })}
        />
      </div>
      <div>
        <label>Difficulty</label>
        <select
          value={filters.difficulty}
          onChange={(evt) => onChange({ ...filters, difficulty: evt.target.value })}
        >
          {difficultyOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label>Min hours</label>
        <input
          type="number"
          min={0}
          step="0.5"
          value={filters.min_hours}
          onChange={(evt) => onChange({ ...filters, min_hours: evt.target.value })}
        />
      </div>
      <div>
        <label>Max hours</label>
        <input
          type="number"
          min={0}
          step="0.5"
          value={filters.max_hours}
          onChange={(evt) => onChange({ ...filters, max_hours: evt.target.value })}
        />
      </div>
    </div>
  );
}
