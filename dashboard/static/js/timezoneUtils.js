/**
 * Timezone Utilities
 * Handles timezone conversions between UTC and user's local timezone
 */

(function() {
  'use strict';

  window.TimezoneUtils = {
    /**
     * Get user's timezone from browser
     */
    getUserTimezone: function() {
      return Intl.DateTimeFormat().resolvedOptions().timeZone;
    },

    /**
     * Convert UTC datetime string to user's local timezone
     * @param {string} utcDatetime - UTC datetime string (e.g., "2025-08-12")
     * @returns {string} Local datetime string in format "YYYY-MM-DD" or "YYYY-MM-DDTHH:MM"
     */
    utcToLocal: function(utcDatetime) {
      if (!utcDatetime) return '';

      try {
        // Parse the UTC datetime
        const date = new Date(utcDatetime + 'Z'); // Add Z to indicate UTC

        // Check if date is valid
        if (isNaN(date.getTime())) return utcDatetime;

        // Format to local timezone
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');

        // Return date only or datetime based on whether time component exists
        if (utcDatetime.includes('T') || utcDatetime.includes(' ')) {
          return `${year}-${month}-${day}T${hours}:${minutes}`;
        }
        return `${year}-${month}-${day}`;
      } catch (error) {
        console.error('[TimezoneUtils] Error converting UTC to local:', error);
        return utcDatetime;
      }
    },

    /**
     * Convert local datetime to UTC for storage
     * @param {string} localDatetime - Local datetime string (e.g., "2025-08-12" or "2025-08-12T14:30")
     * @returns {string} UTC datetime string
     */
    localToUtc: function(localDatetime) {
      if (!localDatetime) return '';

      try {
        // Parse as local time
        const date = new Date(localDatetime);

        // Check if date is valid
        if (isNaN(date.getTime())) return localDatetime;

        // Convert to UTC ISO string
        return date.toISOString().slice(0, 19).replace('T', ' ');
      } catch (error) {
        console.error('[TimezoneUtils] Error converting local to UTC:', error);
        return localDatetime;
      }
    },

    /**
     * Format datetime for display in user's timezone
     * @param {string} utcDatetime - UTC datetime string
     * @param {object} options - Intl.DateTimeFormat options
     * @returns {string} Formatted datetime string
     */
    formatForDisplay: function(utcDatetime, options = {}) {
      if (!utcDatetime) return '';

      try {
        const date = new Date(utcDatetime + (utcDatetime.includes('Z') ? '' : 'Z'));

        if (isNaN(date.getTime())) return utcDatetime;

        const defaultOptions = {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
          ...options
        };

        return new Intl.DateTimeFormat('en-US', defaultOptions).format(date);
      } catch (error) {
        console.error('[TimezoneUtils] Error formatting for display:', error);
        return utcDatetime;
      }
    },

    /**
     * Get date only (no time) in user's timezone
     * @param {string} utcDatetime - UTC datetime string
     * @returns {string} Date in YYYY-MM-DD format
     */
    getDateOnly: function(utcDatetime) {
      if (!utcDatetime) return '';

      try {
        const date = new Date(utcDatetime + (utcDatetime.includes('Z') ? '' : 'Z'));

        if (isNaN(date.getTime())) return utcDatetime;

        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');

        return `${year}-${month}-${day}`;
      } catch (error) {
        console.error('[TimezoneUtils] Error getting date only:', error);
        return utcDatetime;
      }
    }
  };

  // Auto-detect and store user's timezone in localStorage
  try {
    const userTz = window.TimezoneUtils.getUserTimezone();
    localStorage.setItem('userTimezone', userTz);
    console.log('[TimezoneUtils] User timezone detected:', userTz);
  } catch (error) {
    console.error('[TimezoneUtils] Error detecting timezone:', error);
  }

})();
