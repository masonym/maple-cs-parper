// FilterControls.js
import React from 'react';
import styles from '../assets/ItemList.module.css';

const FilterControls = ({ searchTerm, hidePastItems, worldFilter, onSearchTermChange, onHidePastItemsChange, onWorldFilterChange }) => (
    <div className={styles.controlsContainer}>
        <div className={styles.filterButtons}>
            <button
                className={`${styles.filterButton} ${worldFilter === '' ? styles.active : ''}`}
                onClick={() => onWorldFilterChange('')}>
                All Worlds
            </button>
            <button
                className={`${styles.filterButton} ${worldFilter === 'intWorlds' ? styles.active : ''}`}
                onClick={() => onWorldFilterChange('intWorlds')}>
                Interactive Worlds
            </button>
            <button
                className={`${styles.filterButton} ${worldFilter === 'heroWorlds' ? styles.active : ''}`}
                onClick={() => onWorldFilterChange('heroWorlds')}>
                Heroic Worlds
            </button>
        </div>
        <div className={styles.searchBar}>
            <input
                type="text"
                name="search"
                placeholder="Search by name"
                onChange={onSearchTermChange}
                value={searchTerm}
                className={styles.searchInput}
            />
        </div>
        <div className={styles.checkboxContainer}>
            <label className={styles.checkboxLabel}>
                <input
                    type="checkbox"
                    checked={hidePastItems}
                    onChange={onHidePastItemsChange}
                    className={styles.checkboxInput}
                />
                Show Past Items
            </label>
        </div>
    </div>
);

export default FilterControls;