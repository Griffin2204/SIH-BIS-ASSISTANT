import React from 'react';
import './SearchInput.css';
import { Search, X } from 'lucide-react';

export function SearchInput({
  value,
  onChange,
  onClear,
  onSubmit,
  placeholder = 'Search IS standards, products, documentation...',
  size = 'md',
  className = '',
  ...props
}) {
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && onSubmit) {
      onSubmit(value);
    }
  };

  return (
    <div className={`search-input-wrapper search-input-${size} ${className}`}>
      <Search className="search-icon" size={size === 'sm' ? 16 : size === 'lg' ? 22 : 18} />
      <input
        type="text"
        className="search-input"
        value={value}
        onChange={(e) => onChange && onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        {...props}
      />
      {value && (
        <button
          type="button"
          className="search-clear-btn"
          onClick={() => onClear ? onClear() : onChange && onChange('')}
          aria-label="Clear search"
        >
          <X size={size === 'sm' ? 14 : 16} />
        </button>
      )}
    </div>
  );
}

export default SearchInput;
