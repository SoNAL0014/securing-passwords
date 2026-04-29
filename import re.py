import re
import hashlib

password = input("Enter password: ")

score = 0
suggestions = []

# Conditions
if len(password) >= 8:
    score += 1
else:
    suggestions.append("Use at least 8 characters")

if re.search("[A-Z]", password):
    score += 1
else:
    suggestions.append("Add uppercase letter")

if re.search("[a-z]", password):
    score += 1
else:
    suggestions.append("Add lowercase letter")

if re.search("[0-9]", password):
    score += 1
else:
    suggestions.append("Add number")

if re.search("[@#$%^&*!]", password):
    score += 1
else:
    suggestions.append("Add special character")

# Percentage
percentage = score * 20

# Strength
if score <= 2:
    strength = "Weak ❌"
elif score <= 4:
    strength = "Medium ⚠️"
else:
    strength = "Strong ✅"

# OUTPUT
print("\nPassword Strength:", strength)
print("Strength Percentage:", percentage, "%")

if suggestions:
    print("\nSuggestions:")
    for s in suggestions:
        print("-", s)
else:
    print("\nGreat password 💪")

# 🔐 HASHING PART
hashed_password = hashlib.sha256(password.encode()).hexdigest()

print("\nHashed Password (stored securely):")
print(hashed_password)

# 💾 SAVE TO FILE
with open("passwords.txt", "a") as file:
    file.write(hashed_password + "\n")

print("\nPassword saved securely in file ✅")