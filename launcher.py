#!/usr/bin/env python3
"""
OCR to Excel Launcher
Easy entry point to demonstrate the OCR to Excel solution
"""

import sys
import os
from pathlib import Path

def print_banner():
    """Print application banner"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    📄➡️📊 OCR to Excel                        ║
║              Transform Documents to Structured Data          ║
╚══════════════════════════════════════════════════════════════╝
""")

def check_dependencies():
    """Check what dependencies are available"""
    deps = {
        'streamlit': False,
        'pillow': False,
        'pandas': False,
        'pytesseract': False,
        'pdf2image': False
    }
    
    try:
        import streamlit
        deps['streamlit'] = True
    except ImportError:
        pass
    
    try:
        import PIL
        deps['pillow'] = True
    except ImportError:
        pass
        
    try:
        import pandas
        deps['pandas'] = True
    except ImportError:
        pass
        
    try:
        import pytesseract
        deps['pytesseract'] = True
    except ImportError:
        pass
        
    try:
        import pdf2image
        deps['pdf2image'] = True
    except ImportError:
        pass
    
    return deps

def show_capabilities():
    """Show what the application can do"""
    print("🎯 CAPABILITIES:")
    print("  ✅ Smart data extraction from documents")
    print("  ✅ Intelligent field type detection") 
    print("  ✅ Flexible field-to-column mapping")
    print("  ✅ Excel/CSV export functionality")
    print("  ✅ Template system for reusable mappings")
    print("  ✅ Data quality validation")
    print("  ✅ Multiple export formats")

def show_use_cases():
    """Show target use cases"""
    print("\n💼 TARGET USE CASES:")
    print("  • Small Business: Digitize receipts & invoices for accounting")
    print("  • Students: Convert notes, surveys & research data")
    print("  • Teachers: Process grading sheets & attendance lists")  
    print("  • Healthcare: Structure prescriptions & patient records")
    print("  • General: Eliminate manual copy-paste workflows")

def show_value_proposition():
    """Show the value proposition"""
    print("\n💰 VALUE PROPOSITION:")
    print("  📈 Time Savings: Minutes instead of hours")
    print("  🎯 Accuracy: Eliminate transcription errors")
    print("  💵 Cost Effective: Free alternative to expensive OCR tools")
    print("  🚀 Easy to Use: Simple 4-step process")
    print("  📱 Accessible: Works on desktop and mobile")

def run_demo():
    """Run the core functionality demo"""
    print("\n" + "="*60)
    print("🚀 RUNNING CORE FUNCTIONALITY DEMO")
    print("="*60)
    
    try:
        # Import and run the demo
        from demo_ocr import main as demo_main
        return demo_main()
    except ImportError as e:
        print(f"❌ Could not import demo: {e}")
        return 1
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return 1

def launch_streamlit():
    """Launch the Streamlit app"""
    print("\n🌐 Attempting to launch Streamlit app...")
    
    # Check if streamlit is available
    try:
        import streamlit
        print("✅ Streamlit found!")
        print("🚀 Launching web application...")
        print("\n" + "="*60)
        print("📱 The web app will open in your browser")
        print("🌐 URL will be: http://localhost:8501")
        print("⏹️  Press Ctrl+C to stop the server")
        print("="*60)
        
        # Launch streamlit
        os.system("streamlit run ocr_to_excel.py")
        
    except ImportError:
        print("❌ Streamlit not available")
        print("💡 Install with: pip install streamlit pillow pandas openpyxl")
        print("📋 Then run: streamlit run ocr_to_excel.py")
        return False
    
    return True

def show_installation_guide():
    """Show installation instructions"""
    print("\n📦 INSTALLATION GUIDE:")
    print("="*40)
    
    print("\n1️⃣  System Dependencies (Linux/Ubuntu):")
    print("   sudo apt-get update")
    print("   sudo apt-get install tesseract-ocr poppler-utils")
    
    print("\n2️⃣  Python Dependencies:")
    print("   pip install streamlit pillow pandas openpyxl pytesseract pdf2image")
    
    print("\n3️⃣  Launch the App:")
    print("   python launcher.py")
    print("   # or directly:")
    print("   streamlit run ocr_to_excel.py")

def show_menu():
    """Show main menu and handle user choice"""
    while True:
        print("\n" + "="*60)
        print("📋 MAIN MENU")
        print("="*60)
        print("1. 🎪 Run Core Functionality Demo")
        print("2. 🌐 Launch Full Web Application") 
        print("3. 🔍 Check Dependencies")
        print("4. 📦 Show Installation Guide")
        print("5. 📖 Show Documentation")
        print("6. ❌ Exit")
        
        try:
            choice = input("\n👉 Select an option (1-6): ").strip()
            
            if choice == '1':
                result = run_demo()
                if result == 0:
                    print("\n✅ Demo completed successfully!")
                else:
                    print("\n❌ Demo encountered issues")
                input("\n📋 Press Enter to return to menu...")
                
            elif choice == '2':
                if not launch_streamlit():
                    input("\n📋 Press Enter to return to menu...")
                
            elif choice == '3':
                deps = check_dependencies()
                print("\n🔍 DEPENDENCY STATUS:")
                for dep, available in deps.items():
                    status = "✅" if available else "❌"
                    print(f"  {status} {dep}")
                
                missing = [dep for dep, avail in deps.items() if not avail]
                if missing:
                    print(f"\n⚠️  Missing: {', '.join(missing)}")
                    print("💡 See option 4 for installation instructions")
                else:
                    print("\n🎉 All dependencies available!")
                
                input("\n📋 Press Enter to return to menu...")
                
            elif choice == '4':
                show_installation_guide()
                input("\n📋 Press Enter to return to menu...")
                
            elif choice == '5':
                try:
                    if Path("README_OCR.md").exists():
                        with open("README_OCR.md", 'r') as f:
                            content = f.read()
                        print("\n📖 DOCUMENTATION:")
                        print("="*60)
                        print(content[:2000])  # Show first 2000 chars
                        if len(content) > 2000:
                            print("\n... (truncated)")
                            print(f"📄 Full documentation in README_OCR.md ({len(content)} chars)")
                    else:
                        print("❌ Documentation file not found")
                except Exception as e:
                    print(f"❌ Could not read documentation: {e}")
                
                input("\n📋 Press Enter to return to menu...")
                
            elif choice == '6':
                print("\n👋 Thank you for using OCR to Excel!")
                break
                
            else:
                print("❌ Invalid choice. Please select 1-6.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            input("\n📋 Press Enter to continue...")

def main():
    """Main launcher function"""
    print_banner()
    show_capabilities()
    show_use_cases() 
    show_value_proposition()
    
    # Quick dependency check
    deps = check_dependencies()
    available_count = sum(deps.values())
    total_count = len(deps)
    
    print(f"\n📊 SYSTEM STATUS: {available_count}/{total_count} dependencies available")
    
    if available_count == 0:
        print("⚠️  No dependencies installed - running in basic demo mode")
    elif available_count < total_count:
        print("⚠️  Some dependencies missing - limited functionality") 
    else:
        print("🎉 All dependencies available - full functionality!")
    
    # Show menu
    show_menu()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Launcher error: {e}")
        sys.exit(1)