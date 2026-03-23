import { GoogleGenAI, Type } from "@google/genai";
import { DrinkResponse } from "../types";

const apiKey = process.env.GEMINI_API_KEY || "";
const genAI = new GoogleGenAI({ apiKey });

const SYSTEM_PROMPT = `你是一個精通台灣所有手搖飲品牌的專家。
當使用者輸入店名，請提供 10 個熱門推薦品項，分類為：[經典必喝]、[奶茶/鮮奶系]、[清爽原茶/果茶]、[咀嚼控最愛]。
每個品項需包含：品名(name)、推薦原因(description)、黃金比例(best_ratio)、熱量預估(calories: Low/Medium/High)、價格區間(price_range: $/$$/$$$)。
請務必包含店家資訊(shop_info)，包含店名(name)與標語(slogan)。`;

export async function getDrinkRecommendations(shopName: string): Promise<DrinkResponse | null> {
  const response = await genAI.models.generateContent({
    model: "gemini-1.5-flash",
    contents: `請推薦 ${shopName} 的 10 個品項`,
    config: {
      systemInstruction: SYSTEM_PROMPT,
      responseMimeType: "application/json",
      responseSchema: {
        type: Type.OBJECT,
        properties: {
          shop_info: {
            type: Type.OBJECT,
            properties: {
              name: { type: Type.STRING },
              slogan: { type: Type.STRING }
            },
            required: ["name", "slogan"]
          },
          recommendations: {
            type: Type.ARRAY,
            items: {
              type: Type.OBJECT,
              properties: {
                category: { type: Type.STRING },
                items: {
                  type: Type.ARRAY,
                  items: {
                    type: Type.OBJECT,
                    properties: {
                      name: { type: Type.STRING },
                      description: { type: Type.STRING },
                      best_ratio: { type: Type.STRING },
                      calories: { type: Type.STRING, enum: ["Low", "Medium", "High"] },
                      price_range: { type: Type.STRING, enum: ["$", "$$", "$$$"] }
                    },
                    required: ["name", "description", "best_ratio", "calories", "price_range"]
                  }
                }
              },
              required: ["category", "items"]
            }
          }
        },
        required: ["shop_info", "recommendations"]
      },
    },
  });

  try {
    return JSON.parse(response.text);
  } catch (error) {
    console.error("Failed to parse Gemini response:", error);
    return null;
  }
}
