/**
 * Fuzzy matching and alias normalization (RapidFuzz style) for dropdowns and typeaheads.
 */

export const INSTITUTION_ALIASES: Record<string, string[]> = {
  "The University of Texas at Dallas": ["ut dallas", "utd", "u.t. dallas", "texas at dallas"],
  "The University of Texas at Austin": ["ut austin", "utaustin", "u.t. austin", "texas at austin"],
  "Texas A&M University": ["tamu", "texas a and m", "texas a&m"],
  "Massachusetts Institute of Technology": ["mit"],
  "Stanford University": ["stanford"],
  "University of California, Berkeley": ["uc berkeley", "ucb", "cal berkeley", "berkeley"],
  "Carnegie Mellon University": ["cmu", "carnegie mellon"],
  "Georgia Institute of Technology": ["georgia tech", "gatech"],
  "University of Illinois Urbana-Champaign": ["uiuc", "illinois urbana", "university of illinois"],
  "University of Washington": ["uw", "u of w", "u-dub"]
};

export function normalizeString(str: string): string {
  return str.toLowerCase().replace(/[^a-z0-9\s]/g, ' ').replace(/\s+/g, ' ').trim();
}

export function levenshteinDistance(s1: string, s2: string): number {
  const m = s1.length;
  const n = s2.length;
  const dp: number[][] = Array.from({ length: m + 1 }, () => Array(n + 1).fill(0));

  for (let i = 0; i <= m; i++) dp[i][0] = i;
  for (let j = 0; j <= n; j++) dp[0][j] = j;

  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      if (s1[i - 1] === s2[j - 1]) {
        dp[i][j] = dp[i - 1][j - 1];
      } else {
        dp[i][j] = 1 + Math.min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]);
      }
    }
  }
  return dp[m][n];
}

export function stringSimilarity(s1: string, s2: string): number {
  const n1 = normalizeString(s1);
  const n2 = normalizeString(s2);
  if (!n1 && !n2) return 1.0;
  if (!n1 || !n2) return 0.0;
  if (n1 === n2) return 1.0;

  // Check alias lookup
  for (const [canonical, aliases] of Object.entries(INSTITUTION_ALIASES)) {
    const normCanonical = normalizeString(canonical);
    const hasAliasMatch1 = (normCanonical === n1 || aliases.some(a => normalizeString(a) === n1));
    const hasAliasMatch2 = (normCanonical === n2 || aliases.some(a => normalizeString(a) === n2));
    if (hasAliasMatch1 && hasAliasMatch2) {
      return 1.0;
    }
  }

  // Token sort ratio
  const tokens1 = n1.split(' ').sort().join(' ');
  const tokens2 = n2.split(' ').sort().join(' ');
  if (tokens1 === tokens2) return 1.0;

  // Token inclusion check
  if (n1.includes(n2) || n2.includes(n1)) {
    const shorter = Math.min(n1.length, n2.length);
    const longer = Math.max(n1.length, n2.length);
    return 0.85 + 0.15 * (shorter / longer);
  }

  const maxLen = Math.max(n1.length, n2.length);
  const dist = levenshteinDistance(n1, n2);
  return Math.max(0, 1.0 - (dist / maxLen));
}

export interface MatchResult {
  option: HTMLElement;
  text: string;
  score: number;
}

export function findBestMatch(
  target: string, 
  optionElements: HTMLElement[], 
  threshold: number = 0.65
): MatchResult | null {
  let bestScore = -1;
  let bestElem: HTMLElement | null = null;
  let bestText = '';

  for (const elem of optionElements) {
    const text = elem.textContent || '';
    const score = stringSimilarity(target, text);
    if (score > bestScore) {
      bestScore = score;
      bestElem = elem;
      bestText = text;
    }
  }

  if (bestScore >= threshold && bestElem) {
    return {
      option: bestElem,
      text: bestText,
      score: bestScore
    };
  }

  return null;
}
