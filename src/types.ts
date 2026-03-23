export interface DrinkItem {
  name: string;
  description: string;
  best_ratio: string;
  calories: 'Low' | 'Medium' | 'High';
  price_range: '$' | '$$' | '$$$';
}

export interface CategoryGroup {
  category: string;
  items: DrinkItem[];
}

export interface ShopInfo {
  name: string;
  slogan: string;
}

export interface DrinkResponse {
  shop_info: ShopInfo;
  recommendations: CategoryGroup[];
}
