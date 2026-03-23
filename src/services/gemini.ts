import { GoogleGenAI, Type } from "@google/genai";
import { DrinkCategory, DrinkRecommendation } from "../types";

const apiKey = process.env.GEMINI_API_KEY || "";
const genAI = new GoogleGenAI({ apiKey });

export async function getDrinkRecommendations(shopName: string): Promise<DrinkRecommendation[]> {
  const prompt = `你是一位手搖飲專家。請針對「${shopName}」這家飲料店，推薦 4-6 款熱門飲品。
  請將結果分類為：奶茶系、原茶系、咀嚼控。
  每款飲品需要包含：名稱、推薦原因、建議的黃金比例（冰塊甜度）、熱量分級（1-3，1為低、3為高）、價格區間。`;

  const response = await genAI.models.generateContent({
    model: "gemini-3-flash-preview",
    contents: prompt,
    config: {
      responseMimeType: "application/json",
      responseSchema: {
        type: Type.ARRAY,
        items: {
          type: Type.OBJECT,
          properties: {
            id: { type: Type.STRING },
            name: { type: Type.STRING },
            shop: { type: Type.STRING },
            category: { 
              type: Type.STRING, 
              enum: [DrinkCategory.MILK_TEA, DrinkCategory.TEA, DrinkCategory.CHEWY] 
            },
            reason: { type: Type.STRING },
            goldenRatio: { type: Type.STRING },
            calorieLevel: { type: Type.NUMBER },
            priceRange: { type: Type.STRING },
          },
          required: ["id", "name", "shop", "category", "reason", "goldenRatio", "calorieLevel", "priceRange"],
        },
      },
    },
  });

  try {
    const text = response.text;
    return JSON.parse(text);
  } catch (error) {
    console.error("Failed to parse Gemini response:", error);
    return [];
  }
}
