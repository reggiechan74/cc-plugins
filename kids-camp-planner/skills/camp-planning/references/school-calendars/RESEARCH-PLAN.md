# Phase 2: Ontario School Calendar Research Plan

## Objective

Systematically research and pre-save school calendar data (PA days, breaks, start/end dates) for Ontario schools to provide out-of-the-box support for families without requiring them to manually look up dates.

## Priority Tiers

### Tier 1: Major Public Boards (serve ~70% of Ontario students)
These are the highest-impact boards and should be researched first.

| Board | Abbreviation | Region | Status |
|-------|-------------|--------|--------|
| Toronto DSB | TDSB | Toronto | DONE |
| York Region DSB | YRDSB | York Region | DONE |
| Peel DSB | PDSB | Peel Region | DONE |
| Durham DSB | DDSB | Durham Region | DONE |
| Halton DSB | HDSB | Halton Region | DONE |
| Ottawa-Carleton DSB | OCDSB | Ottawa | DONE |
| Toronto CDSB | TCDSB | Toronto (Catholic) | DONE |
| Dufferin-Peel CDSB | DPCDSB | Peel (Catholic) | DONE |
| York CDSB | YCDSB | York (Catholic) | DONE |

### Tier 2: Other GTA and Major City Boards
| Board | Abbreviation | Region | Status |
|-------|-------------|--------|--------|
| Hamilton-Wentworth DSB | HWDSB | Hamilton | DONE |
| Waterloo Region DSB | WRDSB | Waterloo | DONE |
| Simcoe County DSB | SCDSB | Simcoe | DONE |
| Thames Valley DSB | TVDSB | London | DONE |
| Upper Canada DSB | UCDSB | Eastern Ontario | DONE |

### Tier 3: Well-Known Private Schools (Toronto/GTA)
These have non-standard calendars that cause the most planning challenges.

| School | Location | Known Differences | Status |
|--------|----------|-------------------|--------|
| German International School (GIST) | Etobicoke | 2-week March break, fall break, early Sept start | DONE |
| Upper Canada College (UCC) | Toronto | TODO |
| Bishop Strachan School (BSS) | Toronto | TODO |
| Havergal College | Toronto | TODO |
| Crescent School | Toronto | TODO |
| Bayview Glen | Toronto | TODO |
| Toronto French School (TFS) | Toronto | TODO |
| Montcrest School | Toronto | TODO |
| Greenwood College School | Toronto | TODO |
| Royal St. George's College | Toronto | TODO |
| Branksome Hall | Toronto | TODO |
| St. Clement's School | Toronto | TODO |
| De La Salle College | Toronto | TODO |
| Villanova College | King City | TODO |
| Pickering College | Newmarket | TODO |
| Appleby College | Oakville | TODO |
| Ridley College | St. Catharines | TODO |
| Lakefield College School | Lakefield | TODO |

### Tier 4: French/International Schools
| School | Location | Known Differences | Status |
|--------|----------|-------------------|--------|
| Lycee Francais de Toronto | Toronto | French academic calendar patterns | TODO |
| ISOT (International School of Toronto) | Toronto | IB calendar | TODO |
| Fieldstone School | Toronto | TODO |
| Bond Academy | Toronto | TODO |
| Montessori schools (various) | GTA | Often non-standard | TODO |

## Research Methodology

### For Public Boards
1. Navigate to board website → School Year Calendar section
2. Download current year's calendar PDF
3. Extract: PA days (elementary + secondary), holidays, breaks, first/last day
4. Note any board-specific patterns (e.g., some boards have a fall break)
5. Save in `public-boards/[abbreviation].md` format

### For Private Schools
1. Find school website → Parents/Families → School Calendar
2. Download parent calendar (usually PDF)
3. Extract: all dates, PA/PD/in-service days, breaks (note duration!), start/end dates
4. Cross-reference against nearest public board for alignment analysis
5. Note unique patterns (fall break, extended March break, early starts, early dismissals)
6. Save in `private-schools/[abbreviation].md` format

### Data Format
Follow the established format from `tdsb.md` and `gist.md`:
- School metadata header
- Per-year sections with key dates table, PA days table, holidays/breaks table
- Cross-reference table (private schools only)
- Summer coverage window calculation
- Planning notes for families at that school

### Verification
- Compare extracted dates against 2-3 independent sources when possible
- Flag any dates marked "tentative" or "subject to change"
- Note the source document date (some calendars are revised mid-year)

## Maintenance Schedule

School calendars are typically published:
- **Public boards**: May-June for the following year
- **Private schools**: Varies, some as early as March, some as late as September

### Annual Update Process
1. Each July-August, check for new school year calendars
2. Update existing files with new year's data
3. Keep previous year data (families may reference it)
4. Research any newly added Tier 3/4 schools
5. Update cross-reference alignment tables

## Success Metrics

- **Tier 1 complete**: 9 major public boards saved
- **Tier 3 started**: 5+ Toronto private schools saved
- **Coverage**: Pre-saved data available for schools covering >50% of GTA families
- **Accuracy**: All dates verified against official school publications

## Estimated Effort

| Tier | Schools | Time per School | Total |
|------|---------|-----------------|-------|
| Tier 1 | 8 remaining | 15-20 min | 2-3 hours |
| Tier 2 | 5 boards | 15-20 min | 1.5 hours |
| Tier 3 | 17 schools | 20-30 min | 6-9 hours |
| Tier 4 | 4 schools | 20-30 min | 1.5 hours |
| **Total** | **34** | | **11-16 hours** |

## Next Steps

1. Complete Tier 1 public boards (highest impact, most straightforward)
2. Research 5 most prominent Tier 3 private schools (UCC, BSS, Havergal, TFS, Crescent)
3. Evaluate whether a script could automate public board calendar scraping
4. Consider community contributions for school data
