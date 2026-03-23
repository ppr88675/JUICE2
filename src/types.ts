export enum DrinkCategory {
  ALL = '全部',
  MILK_TEA = '奶茶系',
  TEA = '原茶系',
  CHEWY = '咀嚼控',
}

export interface DrinkRecommendation {
  id: string;
  name: string;
  shop: string;
  category: DrinkCategory;
  reason: string;
  goldenRatio: string;
  calorieLevel: 1 | 2 | 3; // 1: Low, 2: Medium, 3: High
  priceRange: string;
}
