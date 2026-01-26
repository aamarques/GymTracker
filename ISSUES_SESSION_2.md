# Issues Tracking - Session 2

**Date:** 2026-01-23
**Status:** IN PROGRESS

---

## Issue 1: Logout Still Shows Filled Fields (HIGH PRIORITY)

**User Report:** "Well the login issue stills. Is like to click BACK in browser when I click on SAIR."

**Analysis:**
- Autocomplete fix was applied
- User says it feels like clicking browser BACK button
- This suggests form might be restoring from browser history, not autofill

**New Hypothesis:** Browser history/cache restoration (bfcache)

**Action Items:**
- [ ] Investigate browser back/forward cache (bfcache)
- [ ] Check if form is being restored from history
- [ ] Test different solution

---

## Issue 2: Exercise Dropdown Needs Sorting and Filter (MEDIUM)

**User Report:** "When the personal trainer is adding a workout, the exercises dropdown must be in alphabetic order and we need a filter by Muscle group"

**Current State:** Exercises appear in database order, no filtering

**Required:**
- Sort exercises alphabetically by name
- Add muscle group filter dropdown

**Files to modify:**
- frontend/js/app.js (workout plan creation)

---

## Issue 3: Workout Not Visible to Personal Trainer (HIGH)

**User Report:** "The workout is created, but doesn't appear to personal, only for client."

**Current State:** Personal trainer creates workout but can't see it

**Investigation needed:**
- Check workout plans API endpoint for personal trainers
- Verify frontend loads workouts for personal trainers
- Check if workouts are filtered by role correctly

---

## Issue 4: Personal Trainer Can't Edit Client Workout (MEDIUM)

**User Report:** "The Personal must be able to change the client workout"

**Required:**
- Add edit functionality for personal trainers to modify client workouts
- Ensure proper permissions

---

## Issue 5: Exercise Names Not Translated (MEDIUM)

**User Report:** "I choose Portuguese language, but the exercises are listed in English"

**Current State:** Exercise names are stored in Portuguese in DB but UI shows in English

**Investigation needed:**
- Check if exercise names are being translated
- Verify i18n configuration for exercise names
- Exercise names might need to be left in original language (not translated)

---

## Issue 6: Client Sees Exercises Page (HIGH)

**User Report:** "When I do a client login, I see the exercises page. This page is only to Personal."

**Current State:** Client role has access to Exercises tab

**Required:**
- Hide Exercises tab/page from client role
- Show only: Dashboard, Active Workout, Cardio, Profile

**Files to modify:**
- frontend/index.html (navigation)
- frontend/js/app.js (role-based UI)
