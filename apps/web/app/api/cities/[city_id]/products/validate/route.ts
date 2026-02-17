import { NextRequest, NextResponse } from 'next/server';
import OpenAI from 'openai';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ city_id: string }> }
) {
  const { city_id } = await params;
  const product = await request.json();

  // If no API key, fall back to mock validation
  if (!process.env.OPENAI_API_KEY) {
    return NextResponse.json(getMockValidations(product));
  }

  try {
    // Use OpenAI to validate the product
    const validations = await validateWithOpenAI(product);
    return NextResponse.json(validations);
  } catch (error: any) {
    console.error('OpenAI validation error:', error);
    
    // Fall back to mock on error
    return NextResponse.json(getMockValidations(product));
  }
}

async function validateWithOpenAI(product: any) {
  const prompt = `Analyze this product listing and provide validation feedback:

Product Details:
- Name: ${product.name || '(empty)'}
- Description: ${product.description || '(empty)'}
- Category: ${product.category || '(empty)'}
- Price: $${product.price || 0}
- Stock: ${product.stock || 0}
- SKU: ${product.sku || '(empty)'}

Provide validation feedback as a JSON array with objects containing:
- field: string (name, description, category, price, stock)
- issue: string (if there's a problem, otherwise null)
- suggestion: string (helpful advice)
- confidence: number (0.0 to 1.0)

Focus on:
1. Name - Is it descriptive and professional? Any typos?
2. Description - Is it detailed enough? Missing key information?
3. Category - Does it match the product? Better alternatives?
4. Price - Is it reasonable? Possible pricing errors?
5. Stock - Any concerns about inventory levels?

Return ONLY valid JSON array, no markdown or explanation.`;

  const completion = await openai.chat.completions.create({
    model: 'gpt-4o-mini',
    messages: [
      {
        role: 'system',
        content: 'You are a product catalog validation expert. Analyze products and provide actionable feedback in JSON format.',
      },
      {
        role: 'user',
        content: prompt,
      },
    ],
    temperature: 0.3,
    max_tokens: 1000,
  });

  const content = completion.choices[0].message.content || '[]';
  
  try {
    // Try to parse as JSON
    const validations = JSON.parse(content);
    
    // Validate structure
    if (Array.isArray(validations)) {
      return validations.filter(v => 
        v.field && 
        v.suggestion && 
        typeof v.confidence === 'number'
      );
    }
    
    return [];
  } catch (parseError) {
    console.error('Failed to parse OpenAI response:', content);
    return [];
  }
}

// Fallback mock validation (same as before)
function getMockValidations(product: any) {
  const validations = [];

  // Name validation
  if (product.name && product.name.length < 5) {
    validations.push({
      field: 'name',
      issue: 'Product name is too short',
      suggestion: 'Consider adding more descriptive details to the product name',
      confidence: 0.85,
    });
  }

  // Price validation
  if (product.price < 1) {
    validations.push({
      field: 'price',
      issue: 'Price seems unusually low',
      suggestion: 'Verify the price is correct. Consider if this should be $' + (product.price * 100).toFixed(2),
      confidence: 0.72,
    });
  }

  if (product.price > 500) {
    validations.push({
      field: 'price',
      issue: 'High-value item',
      suggestion: 'Ensure premium pricing is justified in the description',
      confidence: 0.68,
    });
  }

  // Description validation
  if (product.description && product.description.length < 20) {
    validations.push({
      field: 'description',
      issue: 'Description is too brief',
      suggestion: 'Add more details about features, benefits, and specifications',
      confidence: 0.91,
    });
  }

  // Category suggestion
  if (product.name && product.name.toLowerCase().includes('cable')) {
    if (product.category !== 'Accessories') {
      validations.push({
        field: 'category',
        suggestion: 'Based on the product name, "Accessories" might be a better category',
        confidence: 0.78,
      });
    }
  }

  if (product.name && (product.name.toLowerCase().includes('keyboard') || product.name.toLowerCase().includes('mouse'))) {
    if (product.category !== 'Electronics') {
      validations.push({
        field: 'category',
        suggestion: 'Consider categorizing as "Electronics"',
        confidence: 0.82,
      });
    }
  }

  // Stock validation
  if (product.stock === 0) {
    validations.push({
      field: 'stock',
      issue: 'Product is out of stock',
      suggestion: 'Consider marking as inactive or setting an estimated restock date',
      confidence: 0.65,
    });
  }

  return validations;
}
