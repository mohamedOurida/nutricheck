#!/usr/bin/env python3
"""
Nutricheck Extended - Combined Food Recognition + OCR to Excel
Extending the original Nutricheck food app with OCR to Excel capabilities
"""

import sys
import os
from pathlib import Path

def print_header():
    """Print combined application header"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    🍔👁 Nutricheck Extended                   ║
║         Food Recognition + OCR to Excel in One Platform      ║
╚══════════════════════════════════════════════════════════════╝
""")

def show_applications():
    """Show available applications"""
    print("🚀 AVAILABLE APPLICATIONS:")
    print("="*50)
    print("1️⃣  🍔 Original Food Image Collector")
    print("    • Upload food photos for nutrition database")  
    print("    • Help build AI food recognition models")
    print("    • Contribute to nutrition research")
    print()
    print("2️⃣  📄 OCR to Excel Converter")
    print("    • Transform documents to structured data")
    print("    • Digitize receipts, invoices, forms")
    print("    • Smart field mapping and export")
    print()
    print("3️⃣  🔄 Combined Workflows") 
    print("    • Process food receipts → nutrition tracking")
    print("    • Restaurant bills → expense + nutrition data")
    print("    • Menu scanning → structured food databases")

def launch_food_app():
    """Launch the original food image collector"""
    print("\n🍔 Launching Food Image Collector...")
    
    if Path("food_image_collector.py").exists():
        try:
            import streamlit
            print("🌐 Starting Streamlit app...")
            os.system("streamlit run food_image_collector.py --server.port 8501")
        except ImportError:
            print("❌ Streamlit not available")
            print("💡 Install with: pip install streamlit")
            return False
    else:
        print("❌ food_image_collector.py not found")
        return False
    
    return True

def launch_ocr_app():
    """Launch the OCR to Excel app"""
    print("\n📄 Launching OCR to Excel Converter...")
    
    if Path("ocr_to_excel.py").exists():
        try:
            import streamlit
            print("🌐 Starting Streamlit app...")
            os.system("streamlit run ocr_to_excel.py --server.port 8502")
        except ImportError:
            print("❌ Streamlit not available")
            print("💡 Running demo mode instead...")
            os.system("python demo_ocr.py")
            return True
    else:
        print("❌ ocr_to_excel.py not found")
        return False
    
    return True

def show_combined_use_cases():
    """Show how the apps work together"""
    print("\n🔄 COMBINED USE CASES:")
    print("="*50)
    
    print("🍽️  Restaurant Receipt Processing:")
    print("   1. Photo of restaurant receipt → OCR extraction")
    print("   2. Extract food items + prices → structured data")
    print("   3. Food items → nutrition lookup via food DB")
    print("   4. Combined expense + nutrition tracking")
    
    print("\n🛒 Grocery Receipt Analysis:")
    print("   1. Grocery receipt → OCR processing")
    print("   2. Food items identified → food database")
    print("   3. Nutrition facts + spending analysis")
    print("   4. Budget tracking + meal planning")
    
    print("\n📋 Menu Digitization:")
    print("   1. Restaurant menu photo → OCR extraction") 
    print("   2. Menu items → structured database")
    print("   3. Food images → nutrition classification")
    print("   4. Complete restaurant food database")

def show_menu():
    """Show main menu"""
    while True:
        print("\n" + "="*60)
        print("📋 NUTRICHECK EXTENDED - MAIN MENU")
        print("="*60)
        print("1. 🍔 Launch Food Image Collector")
        print("2. 📄 Launch OCR to Excel Converter")
        print("3. 🎪 Run OCR Demo (no dependencies needed)")
        print("4. 🔄 Show Combined Use Cases")
        print("5. 📖 Show Documentation")
        print("6. ❌ Exit")
        
        try:
            choice = input("\n👉 Select an option (1-6): ").strip()
            
            if choice == '1':
                if not launch_food_app():
                    input("\n📋 Press Enter to return to menu...")
                    
            elif choice == '2':
                if not launch_ocr_app():
                    input("\n📋 Press Enter to return to menu...")
                    
            elif choice == '3':
                print("\n🎪 Running OCR Demo...")
                os.system("python demo_ocr.py")
                input("\n📋 Press Enter to return to menu...")
                
            elif choice == '4':
                show_combined_use_cases()
                input("\n📋 Press Enter to return to menu...")
                
            elif choice == '5':
                # Show documentation for both apps
                docs = []
                if Path("README.md").exists():
                    docs.append(("Food App README", "README.md"))
                if Path("README_OCR.md").exists():
                    docs.append(("OCR App README", "README_OCR.md"))
                
                if docs:
                    print("\n📖 AVAILABLE DOCUMENTATION:")
                    for i, (name, file) in enumerate(docs, 1):
                        print(f"   {i}. {name}")
                    
                    try:
                        doc_choice = input(f"\nSelect documentation (1-{len(docs)}): ").strip()
                        idx = int(doc_choice) - 1
                        if 0 <= idx < len(docs):
                            _, file = docs[idx]
                            with open(file, 'r') as f:
                                content = f.read()
                            print(f"\n📄 {file}:")
                            print("="*60)
                            print(content[:2000])
                            if len(content) > 2000:
                                print("\n... (truncated)")
                    except (ValueError, IndexError):
                        print("❌ Invalid selection")
                else:
                    print("❌ No documentation found")
                
                input("\n📋 Press Enter to return to menu...")
                
            elif choice == '6':
                print("\n👋 Thank you for using Nutricheck Extended!")
                break
                
            else:
                print("❌ Invalid choice. Please select 1-6.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main function"""
    print_header()
    show_applications()
    
    print("\n💡 WHY COMBINE THESE APPS?")
    print("="*30)
    print("• Unified platform for document + food processing")
    print("• Shared infrastructure reduces development costs") 
    print("• Cross-pollination of user bases")
    print("• Enhanced value proposition for users")
    print("• Data synergies (food receipts = expense + nutrition)")
    
    show_menu()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Extended app error: {e}")
        sys.exit(1)