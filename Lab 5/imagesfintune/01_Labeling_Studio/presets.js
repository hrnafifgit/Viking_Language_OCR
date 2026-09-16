/**
 * presets.js - Character Sets & Class Presets for Ancient Inscriptions & Vision Tasks
 */

// Distinct high-contrast palette for visual distinction between classes
export const PALETTE = [
  '#00f5d4', '#7b2cbf', '#fee440', '#f72585', '#4cc9f0',
  '#ff9e00', '#52b788', '#e63946', '#9d4edd', '#06d6a0',
  '#ff006e', '#8338ec', '#3a86ff', '#fb5607', '#ffbe0b',
  '#2a9d8f', '#e76f51', '#70e000', '#38b000', '#007200',
  '#d00000', '#9d0208', '#6a040f', '#03045e', '#023e8a',
  '#0077b6', '#0096c7', '#00b4d8', '#48cae4', '#90e0ef',
  '#ff0a54', '#ff477e', '#ff70a6', '#ff99c8', '#fec7d7',
  '#f4a261', '#e9c46a', '#a8dadc', '#457b9d', '#1d3557'
];

export function getClassColor(id) {
  return PALETTE[id % PALETTE.length];
}

// 1. Nabataean Alphabet Preset (40 items: 31 letters + 9 numbers)
export const NABATAEAN_CLASSES = [
  { id: 0, char: '𐢀', name_ar: 'ألف نهائية (ـا)', name_en: 'FINAL_ALEPH', unicode: 'U+10880', type: 'letter' },
  { id: 1, char: '𐢁', name_ar: 'ألف مفردة (ا)', name_en: 'ALEPH', unicode: 'U+10881', type: 'letter' },
  { id: 2, char: '𐢂', name_ar: 'باء نهائية (ـب)', name_en: 'FINAL_BETH', unicode: 'U+10882', type: 'letter' },
  { id: 3, char: '𐢃', name_ar: 'باء مفردة (ب)', name_en: 'BETH', unicode: 'U+10883', type: 'letter' },
  { id: 4, char: '𐢄', name_ar: 'جيم (ج)', name_en: 'GIMEL', unicode: 'U+10884', type: 'letter' },
  { id: 5, char: '𐢅', name_ar: 'دال (د)', name_en: 'DALETH', unicode: 'U+10885', type: 'letter' },
  { id: 6, char: '𐢆', name_ar: 'هاء نهائية (ـه)', name_en: 'FINAL_HE', unicode: 'U+10886', type: 'letter' },
  { id: 7, char: '𐢇', name_ar: 'هاء مفردة (هـ)', name_en: 'HE', unicode: 'U+10887', type: 'letter' },
  { id: 8, char: '𐢈', name_ar: 'واو (و)', name_en: 'WAW', unicode: 'U+10888', type: 'letter' },
  { id: 9, char: '𐢉', name_ar: 'زاي (ز)', name_en: 'ZAYIN', unicode: 'U+10889', type: 'letter' },
  { id: 10, char: '𐢊', name_ar: 'حاء (ح)', name_en: 'HETH', unicode: 'U+1088A', type: 'letter' },
  { id: 11, char: '𐢋', name_ar: 'طاء (ط)', name_en: 'TETH', unicode: 'U+1088B', type: 'letter' },
  { id: 12, char: '𐢌', name_ar: 'ياء نهائية (ـي)', name_en: 'FINAL_YODH', unicode: 'U+1088C', type: 'letter' },
  { id: 13, char: '𐢍', name_ar: 'ياء مفردة (ي)', name_en: 'YODH', unicode: 'U+1088D', type: 'letter' },
  { id: 14, char: '𐢎', name_ar: 'كاف نهائية (ـك)', name_en: 'FINAL_KAPH', unicode: 'U+1088E', type: 'letter' },
  { id: 15, char: '𐢏', name_ar: 'كاف مفردة (ك)', name_en: 'KAPH', unicode: 'U+1088F', type: 'letter' },
  { id: 16, char: '𐢐', name_ar: 'لام نهائية (ـل)', name_en: 'FINAL_LAMEDH', unicode: 'U+10890', type: 'letter' },
  { id: 17, char: '𐢑', name_ar: 'لام مفردة (ل)', name_en: 'LAMEDH', unicode: 'U+10891', type: 'letter' },
  { id: 18, char: '𐢒', name_ar: 'ميم نهائية (ـم)', name_en: 'FINAL_MEM', unicode: 'U+10892', type: 'letter' },
  { id: 19, char: '𐢓', name_ar: 'ميم مفردة (م)', name_en: 'MEM', unicode: 'U+10893', type: 'letter' },
  { id: 20, char: '𐢔', name_ar: 'نون نهائية (ـن)', name_en: 'FINAL_NUN', unicode: 'U+10894', type: 'letter' },
  { id: 21, char: '𐢕', name_ar: 'نون مفردة (ن)', name_en: 'NUN', unicode: 'U+10895', type: 'letter' },
  { id: 22, char: '𐢖', name_ar: 'سمخ / سين (س)', name_en: 'SAMEKH', unicode: 'U+10896', type: 'letter' },
  { id: 23, char: '𐢗', name_ar: 'عين (ع)', name_en: 'AYIN', unicode: 'U+10897', type: 'letter' },
  { id: 24, char: '𐢘', name_ar: 'فاء (ف)', name_en: 'PE', unicode: 'U+10898', type: 'letter' },
  { id: 25, char: '𐢙', name_ar: 'صاد (ص)', name_en: 'SADHE', unicode: 'U+10899', type: 'letter' },
  { id: 26, char: '𐢚', name_ar: 'قاف (ق)', name_en: 'QOPH', unicode: 'U+1089A', type: 'letter' },
  { id: 27, char: '𐢛', name_ar: 'راء (ر)', name_en: 'RESH', unicode: 'U+1089B', type: 'letter' },
  { id: 28, char: '𐢜', name_ar: 'شين نهائية (ـش)', name_en: 'FINAL_SHIN', unicode: 'U+1089C', type: 'letter' },
  { id: 29, char: '𐢝', name_ar: 'شين مفردة (ش)', name_en: 'SHIN', unicode: 'U+1089D', type: 'letter' },
  { id: 30, char: '𐢞', name_ar: 'تاء (ت)', name_en: 'TAW', unicode: 'U+1089E', type: 'letter' },
  { id: 31, char: '𐢧', name_ar: 'رقم 1', name_en: 'NUMBER_ONE', unicode: 'U+108A7', type: 'number' },
  { id: 32, char: '𐢨', name_ar: 'رقم 2', name_en: 'NUMBER_TWO', unicode: 'U+108A8', type: 'number' },
  { id: 33, char: '𐢩', name_ar: 'رقم 3', name_en: 'NUMBER_THREE', unicode: 'U+108A9', type: 'number' },
  { id: 34, char: '𐢪', name_ar: 'رقم 4', name_en: 'NUMBER_FOUR', unicode: 'U+108AA', type: 'number' },
  { id: 35, char: '𐢫', name_ar: 'رقم 4 صليبي', name_en: 'CRUCIFORM_FOUR', unicode: 'U+108AB', type: 'number' },
  { id: 36, char: '𐢬', name_ar: 'رقم 5', name_en: 'NUMBER_FIVE', unicode: 'U+108AC', type: 'number' },
  { id: 37, char: '𐢭', name_ar: 'رقم 10', name_en: 'NUMBER_TEN', unicode: 'U+108AD', type: 'number' },
  { id: 38, char: '𐢮', name_ar: 'رقم 20', name_en: 'NUMBER_TWENTY', unicode: 'U+108AE', type: 'number' },
  { id: 39, char: '𐢯', name_ar: 'رقم 100', name_en: 'NUMBER_HUNDRED', unicode: 'U+108AF', type: 'number' }
];

// 2. Aramaic Imperial Alphabet Preset
export const ARAMAIC_CLASSES = [
  { id: 0, char: '𐡀', name_ar: 'ألف (آرامية)', name_en: 'ARAMAIC_ALEPH', unicode: 'U+10840', type: 'letter' },
  { id: 1, char: '𐡁', name_ar: 'باء', name_en: 'ARAMAIC_BETH', unicode: 'U+10841', type: 'letter' },
  { id: 2, char: '𐡂', name_ar: 'جيم', name_en: 'ARAMAIC_GIMEL', unicode: 'U+10842', type: 'letter' },
  { id: 3, char: '𐡃', name_ar: 'دال', name_en: 'ARAMAIC_DALETH', unicode: 'U+10843', type: 'letter' },
  { id: 4, char: '𐡄', name_ar: 'هاء', name_en: 'ARAMAIC_HE', unicode: 'U+10844', type: 'letter' },
  { id: 5, char: '𐡅', name_ar: 'واو', name_en: 'ARAMAIC_WAW', unicode: 'U+10845', type: 'letter' },
  { id: 6, char: '𐡆', name_ar: 'زاي', name_en: 'ARAMAIC_ZAYIN', unicode: 'U+10846', type: 'letter' },
  { id: 7, char: '𐡇', name_ar: 'حاء', name_en: 'ARAMAIC_HETH', unicode: 'U+10847', type: 'letter' },
  { id: 8, char: '𐡈', name_ar: 'طاء', name_en: 'ARAMAIC_TETH', unicode: 'U+10848', type: 'letter' },
  { id: 9, char: '𐡉', name_ar: 'ياء', name_en: 'ARAMAIC_YODH', unicode: 'U+10849', type: 'letter' },
  { id: 10, char: '𐡊', name_ar: 'كاف', name_en: 'ARAMAIC_KAPH', unicode: 'U+1084A', type: 'letter' },
  { id: 11, char: '𐡋', name_ar: 'لام', name_en: 'ARAMAIC_LAMEDH', unicode: 'U+1084B', type: 'letter' },
  { id: 12, char: '𐡌', name_ar: 'ميم', name_en: 'ARAMAIC_MEM', unicode: 'U+1084C', type: 'letter' },
  { id: 13, char: '𐡍', name_ar: 'نون', name_en: 'ARAMAIC_NUN', unicode: 'U+1084D', type: 'letter' },
  { id: 14, char: '𐡎', name_ar: 'سمخ', name_en: 'ARAMAIC_SAMEKH', unicode: 'U+1084E', type: 'letter' },
  { id: 15, char: '𐡏', name_ar: 'عين', name_en: 'ARAMAIC_AYIN', unicode: 'U+1084F', type: 'letter' },
  { id: 16, char: '𐡐', name_ar: 'فاء / پي', name_en: 'ARAMAIC_PE', unicode: 'U+10850', type: 'letter' },
  { id: 17, char: '𐡑', name_ar: 'صاد', name_en: 'ARAMAIC_SADHE', unicode: 'U+10851', type: 'letter' },
  { id: 18, char: '𐡒', name_ar: 'قاف', name_en: 'ARAMAIC_QOPH', unicode: 'U+10852', type: 'letter' },
  { id: 19, char: '𐡓', name_ar: 'راء', name_en: 'ARAMAIC_RESH', unicode: 'U+10853', type: 'letter' },
  { id: 20, char: '𐡔', name_ar: 'شين', name_en: 'ARAMAIC_SHIN', unicode: 'U+10854', type: 'letter' },
  { id: 21, char: '𐡕', name_ar: 'تاء', name_en: 'ARAMAIC_TAW', unicode: 'U+10855', type: 'letter' },
  { id: 22, char: '𐡘', name_ar: 'رقم 1', name_en: 'ARAMAIC_NUM_1', unicode: 'U+10858', type: 'number' },
  { id: 23, char: '𐡙', name_ar: 'رقم 2', name_en: 'ARAMAIC_NUM_2', unicode: 'U+10859', type: 'number' },
  { id: 24, char: '𐡚', name_ar: 'رقم 3', name_en: 'ARAMAIC_NUM_3', unicode: 'U+1085A', type: 'number' },
  { id: 25, char: '𐡛', name_ar: 'رقم 10', name_en: 'ARAMAIC_NUM_10', unicode: 'U+1085B', type: 'number' },
  { id: 26, char: '𐡜', name_ar: 'رقم 20', name_en: 'ARAMAIC_NUM_20', unicode: 'U+1085C', type: 'number' },
  { id: 27, char: '𐡝', name_ar: 'رقم 100', name_en: 'ARAMAIC_NUM_100', unicode: 'U+1085D', type: 'number' }
];

// 3. Arabic Standard Alphabet Preset
export const ARABIC_CLASSES = [
  'أ', 'ب', 'ت', 'ث', 'ج', 'ح', 'خ', 'د', 'ذ', 'ر', 'ز', 'س', 'ش', 'ص',
  'ض', 'ط', 'ظ', 'ع', 'غ', 'ف', 'ق', 'ك', 'ل', 'م', 'ن', 'هـ', 'و', 'ي'
].map((char, index) => ({
  id: index,
  char: char,
  name_ar: `حرف ${char}`,
  name_en: `ARABIC_${char}`,
  unicode: `U+${char.charCodeAt(0).toString(16).toUpperCase()}`,
  type: 'letter'
}));

/**
 * Intelligent file parser: reads raw string content from .txt, .json, .yaml, .csv
 * and converts it into a normalized list of class objects.
 */
export function parseClassesFile(rawContent, filename = '') {
  const content = rawContent.trim();
  if (!content) return [];

  // Try JSON
  if (filename.endsWith('.json') || (content.startsWith('[') && content.endsWith(']')) || (content.startsWith('{') && content.endsWith('}'))) {
    try {
      const parsed = JSON.parse(content);
      if (Array.isArray(parsed)) {
        return parsed.map((item, idx) => {
          if (typeof item === 'string') {
            return { id: idx, char: item, name_ar: item, name_en: item, type: 'custom' };
          }
          return {
            id: item.id !== undefined ? item.id : idx,
            char: item.char || item.symbol || item.name || `${idx}`,
            name_ar: item.name_ar || item.name || item.char || `فئة ${idx}`,
            name_en: item.name_en || item.name || item.char || `Class ${idx}`,
            unicode: item.unicode || '',
            type: item.type || 'custom'
          };
        });
      }
    } catch (e) {
      console.warn('JSON parse fallback to text parser:', e);
    }
  }

  // Parse lines for text / YAML / CSV formats
  const lines = content.split(/\r?\n/).map(l => l.trim()).filter(l => l.length > 0 && !l.startsWith('#'));
  const parsedClasses = [];

  lines.forEach((line, idx) => {
    // Check if YAML list line (e.g. "  - class_name" or "0: class_name")
    let cleanLine = line.replace(/^-\s*/, '').replace(/^\d+:\s*/, '').trim();

    // Check pattern: "𐢀 (ألف نهائية)" or "𐢀 | FINAL_ALEPH | ألف نهائية"
    const parenMatch = cleanLine.match(/^(\S+)\s*\((.+?)\)$/);
    const pipeMatch = cleanLine.split('|').map(s => s.trim());

    if (parenMatch) {
      const char = parenMatch[1];
      const desc = parenMatch[2];
      parsedClasses.push({
        id: idx,
        char: char,
        name_ar: desc,
        name_en: desc,
        unicode: char.length > 0 ? `U+${char.codePointAt(0).toString(16).toUpperCase()}` : '',
        type: 'custom'
      });
    } else if (pipeMatch.length >= 2) {
      const char = pipeMatch[0];
      const name_en = pipeMatch[1] || char;
      const name_ar = pipeMatch[2] || name_en;
      parsedClasses.push({
        id: idx,
        char: char,
        name_ar: name_ar,
        name_en: name_en,
        unicode: char.length > 0 ? `U+${char.codePointAt(0).toString(16).toUpperCase()}` : '',
        type: 'custom'
      });
    } else {
      // Single token or word per line (like classes.txt or classes_arabic.txt)
      parsedClasses.push({
        id: idx,
        char: cleanLine,
        name_ar: cleanLine,
        name_en: cleanLine,
        unicode: cleanLine.length === 1 || cleanLine.length === 2 ? `U+${cleanLine.codePointAt(0).toString(16).toUpperCase()}` : '',
        type: 'custom'
      });
    }
  });

  return parsedClasses;
}
