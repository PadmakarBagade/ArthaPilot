• The LLM never calculates money. All numbers come from tested Python functions. The LLM only chooses tools and explains verified results.
• Every number shown to the user must carry an evidence reference (transaction IDs or the formula used).
• Every answer has three separate sections: Observed Fact, Prediction (with confidence), Recommendation (with simulated impact).
• All money is stored as integer paise (₹1 = 100 paise) to avoid floating-point errors.
• Every module gets unit tests. No phase is finished until its tests pass.
• Never commit real user data. Real statements live only in data/private/, which is git-ignored.
• Mask personal data (names, account numbers, phone numbers, UPI IDs) before anything is sent to the LLM.