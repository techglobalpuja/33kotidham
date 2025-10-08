#!/usr/bin/env python3
"""
Script to add dummy blog data with real spiritual content and images
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database get_db, engine
from app.models import Blog, Category, User, UserRole
from app.auth import get_password_hash
from datetime import datetime, timedelta
import requests
from PIL import Image
import uuid

def create_admin_user(db: Session):
    """Create an admin user if not exists"""
    admin = db.query(User).filter(User.role == UserRole.ADMIN.value).first()
    if not admin:
        admin = User(
            name="Blog Admin",
            email="admin@33kotidham.com",
            mobile="9999999999",
            password=get_password_hash("admin123"),
            role=UserRole.ADMIN.value,
            is_active=True,
            email_verified=True
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
    return admin

def download_and_save_image(url: str, filename: str) -> str:
    """Download image from URL and save locally"""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # Create uploads/images directory if not exists
            os.makedirs("uploads/images", exist_ok=True)
            
            file_path = f"uploads/images/{filename}"
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            # Optimize image
            with Image.open(file_path) as img:
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                # Resize if too large
                if img.width > 1200:
                    ratio = 1200 / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((1200, new_height), Image.Resampling.LANCZOS)
                
                img.save(file_path, optimize=True, quality=85)
            
            return file_path
    except Exception as e:
        print(f"Error downloading image {url}: {e}")
        return None

def create_categories(db: Session):
    """Create blog categories"""
    categories_data = [
        {
            "name": "Spiritual Guidance",
            "description": "Articles about spiritual practices and guidance",
            "is_active": True
        },
        {
            "name": "Temple Stories",
            "description": "Stories and histories of famous temples",
            "is_active": True
        },
        {
            "name": "Puja Rituals",
            "description": "Information about various puja ceremonies",
            "is_active": True
        },
        {
            "name": "Festival Celebrations",
            "description": "Hindu festivals and their significance",
            "is_active": True
        },
        {
            "name": "Sacred Places",
            "description": "Information about holy places and pilgrimages",
            "is_active": True
        }
    ]
    
    categories = []
    for cat_data in categories_data:
        existing = db.query(Category).filter(Category.name == cat_data["name"]).first()
        if not existing:
            category = Category(**cat_data)
            db.add(category)
            categories.append(category)
        else:
            categories.append(existing)
    
    db.commit()
    return categories

def create_dummy_blogs(db: Session, admin_user: User, categories: list):
    """Create dummy blog posts with real content"""
    
    # Sample image URLs (using placeholder images with spiritual themes)
    sample_images = [
        "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?w=800&h=600&fit=crop",  # Temple
        "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800&h=600&fit=crop",  # Prayer
        "https://images.unsplash.com/photo-1509233725247-49e657c54213?w=800&h=600&fit=crop",  # Ganga Aarti
        "https://images.unsplash.com/photo-1544735716-392fe2489ffa?w=800&h=600&fit=crop",  # Hindu Temple
        "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&h=600&fit=crop",  # Meditation
    ]
    
    blogs_data = [
        {
            "title": "The Sacred Power of Ganga Aarti",
            "subtitle": "Experience Divine Bliss at Varanasi's Holy Ghats",
            "content": """
            <div class="blog-content">
                <img src="uploads/images/ganga-aarti.jpg" alt="Ganga Aarti Ceremony" class="blog-image" />
                <p>The evening Ganga Aarti at Varanasi is one of the most mesmerizing spiritual experiences one can witness. As the sun sets over the sacred Ganges, thousands of devotees gather at the ghats to participate in this ancient ritual of worship.</p>
                
                <h3>The Significance of Ganga Aarti</h3>
                <p>Ganga Aarti is not just a ceremony; it's a divine communion with Mother Ganga. The ritual involves offering prayers through fire, flowers, and sacred chants. The synchronized movements of the priests, the sound of bells, and the fragrance of incense create an atmosphere of pure devotion.</p>
                
                <h3>When and Where</h3>
                <p>The main Ganga Aarti takes place at Dashashwamedh Ghat every evening at sunset. The ceremony lasts for about 45 minutes and is performed by young pandits who have been trained in this sacred art.</p>
                
                <blockquote>
                "गंगे च यमुने चैव गोदावरि सरस्वति। नर्मदे सिन्धु कावेरि जलेऽस्मिन् संनिधिं कुरु॥"
                </blockquote>
                
                <p>Witnessing the Ganga Aarti is believed to cleanse one's sins and bring spiritual purification. The divine energy that flows during this ceremony is said to transform the hearts of all who participate with true devotion.</p>
            </div>
            """,
            "meta_description": "Experience the divine Ganga Aarti ceremony at Varanasi. Learn about its significance, timing, and spiritual benefits in this comprehensive guide.",
            "tags": "ganga aarti,varanasi,spiritual,hinduism,river worship,dashashwamedh ghat",
            "category_id": 1,  # Spiritual Guidance
            "is_featured": True,
            "is_active": True,
            "publish_time": datetime.now() - timedelta(days=5),
            "image_url": sample_images[2]
        },
        {
            "title": "Kedarnath Temple: Journey to the Abode of Lord Shiva",
            "subtitle": "A Pilgrimage Through the Majestic Himalayas",
            "content": """
            <div class="blog-content">
                <img src="uploads/images/kedarnath-temple.jpg" alt="Kedarnath Temple" class="blog-image" />
                <p>Nestled in the breathtaking Garhwal Himalayas at an altitude of 3,583 meters, Kedarnath Temple stands as one of the most revered shrines dedicated to Lord Shiva. This ancient temple, part of the Char Dham Yatra, attracts millions of devotees every year who brave the challenging journey to seek divine blessings.</p>
                
                <h3>The Legend of Kedarnath</h3>
                <p>According to Hindu mythology, Kedarnath is where Lord Shiva took refuge in the form of a bull to avoid the Pandavas. When discovered, he dived into the ground, leaving behind his hump, which is worshipped as the sacred lingam in the temple.</p>
                
                <h3>The Sacred Architecture</h3>
                <p>Built using massive stone slabs over a large rectangular platform, the temple showcases ancient architectural brilliance. The conical-shaped roof and the intricate carvings reflect the devotion and craftsmanship of our ancestors.</p>
                
                <h3>Planning Your Visit</h3>
                <ul>
                    <li><strong>Best Time:</strong> May to October</li>
                    <li><strong>Trek Distance:</strong> 16 km from Gaurikund</li>
                    <li><strong>Helicopter Services:</strong> Available from Phata and Sersi</li>
                    <li><strong>Accommodation:</strong> Various guesthouses and ashrams available</li>
                </ul>
                
                <p>The journey to Kedarnath is not just a physical pilgrimage but a spiritual transformation. The pristine beauty of the Himalayas, combined with the divine energy of Lord Shiva, creates an unforgettable experience of devotion and inner peace.</p>
            </div>
            """,
            "meta_description": "Plan your pilgrimage to Kedarnath Temple, one of the holiest Shiva shrines. Complete guide with travel tips, best time to visit, and spiritual significance.",
            "tags": "kedarnath,lord shiva,char dham,himalayan temples,pilgrimage,uttarakhand",
            "category_id": 2,  # Temple Stories
            "is_featured": True,
            "is_active": True,
            "publish_time": datetime.now() - timedelta(days=10),
            "image_url": sample_images[3]
        },
        {
            "title": "Diwali: The Festival of Lights and Inner Illumination",
            "subtitle": "Celebrating Victory of Light Over Darkness",
            "content": """
            <div class="blog-content">
                <img src="uploads/images/diwali-celebration.jpg" alt="Diwali Lights" class="blog-image" />
                <p>Diwali, also known as Deepavali, is the most celebrated festival in Hindu culture. This five-day festival of lights symbolizes the victory of light over darkness, good over evil, and knowledge over ignorance. Each flickering diya (oil lamp) represents hope, prosperity, and spiritual awakening.</p>
                
                <h3>The Five Days of Diwali</h3>
                <ol>
                    <li><strong>Dhanteras:</strong> Worship of wealth and prosperity</li>
                    <li><strong>Choti Diwali:</strong> Preparation and cleansing</li>
                    <li><strong>Diwali:</strong> Main celebration with Lakshmi Puja</li>
                    <li><strong>Govardhan Puja:</strong> Worship of Lord Krishna</li>
                    <li><strong>Bhai Dooj:</strong> Celebration of sibling bond</li>
                </ol>
                
                <h3>Spiritual Significance</h3>
                <p>Beyond the festivities, Diwali holds deep spiritual meaning. It commemorates Lord Rama's return to Ayodhya after 14 years of exile and his victory over the demon king Ravana. The lighting of diyas represents the removal of spiritual darkness and the awakening of inner light.</p>
                
                <h3>Traditional Celebrations</h3>
                <p>Families clean and decorate their homes, create beautiful rangoli patterns, prepare delicious sweets, and exchange gifts. The evening Lakshmi Puja is performed to invite prosperity and abundance into homes.</p>
                
                <div class="quote-box">
                    <p><em>"As we light the diyas outside, let us also light the lamp of love, compassion, and understanding within our hearts."</em></p>
                </div>
                
                <p>Diwali teaches us that no matter how dark the night, dawn will always come. It reminds us to be the light in someone else's darkness and to spread joy, peace, and positivity wherever we go.</p>
            </div>
            """,
            "meta_description": "Discover the spiritual significance of Diwali, the Festival of Lights. Learn about traditions, celebrations, and the deeper meaning behind this sacred festival.",
            "tags": "diwali,festival of lights,lakshmi puja,hindu festivals,spirituality,celebration",
            "category_id": 4,  # Festival Celebrations
            "is_featured": False,
            "is_active": True,
            "publish_time": datetime.now() - timedelta(days=3),
            "image_url": sample_images[1]
        },
        {
            "title": "The Art of Morning Meditation: Starting Your Day with Divine Connection",
            "subtitle": "Transform Your Life Through Sacred Morning Practice",
            "content": """
            <div class="blog-content">
                <img src="uploads/images/morning-meditation.jpg" alt="Morning Meditation" class="blog-image" />
                <p>In the stillness of early morning, when the world is just awakening, lies the perfect opportunity for spiritual connection. Morning meditation is an ancient practice that has been followed by sages and spiritual seekers for thousands of years to achieve inner peace and divine realization.</p>
                
                <h3>Why Meditate in the Morning?</h3>
                <p>The early morning hours, known as 'Brahma Muhurta' (approximately 4:00-6:00 AM), are considered the most auspicious time for spiritual practices. During these hours:</p>
                <ul>
                    <li>The mind is naturally calm and clear</li>
                    <li>There are fewer distractions</li>
                    <li>The energy in nature is pure and conducive to meditation</li>
                    <li>It sets a positive tone for the entire day</li>
                </ul>
                
                <h3>Simple Steps to Begin</h3>
                <ol>
                    <li><strong>Find a Quiet Space:</strong> Choose a clean, peaceful corner in your home</li>
                    <li><strong>Comfortable Posture:</strong> Sit with your spine straight, shoulders relaxed</li>
                    <li><strong>Focus on Breath:</strong> Begin with simple breathing awareness</li>
                    <li><strong>Chant a Mantra:</strong> Use "Om" or any sacred mantra</li>
                    <li><strong>Start Small:</strong> Begin with 10-15 minutes daily</li>
                </ol>
                
                <h3>Benefits of Regular Practice</h3>
                <p>Regular morning meditation brings numerous benefits:</p>
                <ul>
                    <li>Reduced stress and anxiety</li>
                    <li>Improved concentration and clarity</li>
                    <li>Enhanced emotional stability</li>
                    <li>Deeper spiritual connection</li>
                    <li>Increased energy throughout the day</li>
                </ul>
                
                <blockquote>
                "योगस्थः कुरु कर्माणि संगं त्यक्त्वा धनंजय। सिद्ध्यसिद्ध्योः समो भूत्वा समत्वं योग उच्यते॥" - Bhagavad Gita
                </blockquote>
                
                <p>Remember, meditation is not about stopping thoughts but observing them without judgment. Be patient with yourself and allow the practice to unfold naturally. Each moment of mindfulness is a step closer to inner peace and spiritual awakening.</p>
            </div>
            """,
            "meta_description": "Learn the art of morning meditation to transform your daily life. Discover benefits, techniques, and tips for establishing a meaningful spiritual practice.",
            "tags": "meditation,morning practice,spirituality,mindfulness,brahma muhurta,inner peace",
            "category_id": 1,  # Spiritual Guidance
            "is_featured": False,
            "is_active": True,
            "publish_time": datetime.now() - timedelta(days=7),
            "image_url": sample_images[4]
        },
        {
            "title": "Rudrabhishek: The Sacred Bathing Ritual of Lord Shiva",
            "subtitle": "Understanding the Power and Significance of This Ancient Puja",
            "content": """
            <div class="blog-content">
                <img src="uploads/images/rudrabhishek.jpg" alt="Rudrabhishek Ceremony" class="blog-image" />
                <p>Rudrabhishek is one of the most powerful and sacred rituals dedicated to Lord Shiva. This ancient puja involves the ceremonial bathing of the Shiva lingam with various sacred substances while chanting the Rudra mantras. It is believed to be one of the most effective ways to seek Lord Shiva's blessings and grace.</p>
                
                <h3>What is Rudrabhishek?</h3>
                <p>The word 'Rudrabhishek' combines 'Rudra' (another name for Lord Shiva) and 'Abhishek' (ritual bathing). This ceremony involves offering water, milk, honey, yogurt, ghee, and other sacred substances to the Shiva lingam while reciting powerful Vedic mantras.</p>
                
                <h3>Sacred Substances Used</h3>
                <ul>
                    <li><strong>Water:</strong> Purification and spiritual cleansing</li>
                    <li><strong>Milk:</strong> Nourishment and maternal love</li>
                    <li><strong>Honey:</strong> Sweetness and divine nectar</li>
                    <li><strong>Yogurt:</strong> Cooling and calming energy</li>
                    <li><strong>Ghee:</strong> Illumination and spiritual light</li>
                    <li><strong>Sugar:</strong> Joy and happiness</li>
                    <li><strong>Rose Water:</strong> Love and devotion</li>
                </ul>
                
                <h3>Benefits of Rudrabhishek</h3>
                <p>Regular performance of Rudrabhishek is said to bring:</p>
                <ul>
                    <li>Removal of negative energies and obstacles</li>
                    <li>Peace and harmony in family life</li>
                    <li>Success in business and career</li>
                    <li>Healing from diseases and ailments</li>
                    <li>Spiritual growth and enlightenment</li>
                    <li>Fulfillment of desires and wishes</li>
                </ul>
                
                <h3>Best Times for Rudrabhishek</h3>
                <p>While Rudrabhishek can be performed any time, certain occasions are considered especially auspicious:</p>
                <ul>
                    <li>Mondays (Somwar)</li>
                    <li>Maha Shivratri</li>
                    <li>Shravan month</li>
                    <li>Solar and lunar eclipses</li>
                    <li>Personal important occasions</li>
                </ul>
                
                <div class="mantra-box">
                    <h4>Sacred Rudrabhishek Mantra:</h4>
                    <p><em>ॐ नमः शिवाय नमः शिवाय नमः शिवाय नमः शिवाय</em></p>
                </div>
                
                <p>The vibrations created by the mantras during Rudrabhishek create a powerful spiritual atmosphere that can transform the consciousness of both the performer and the surroundings. This ancient ritual continues to be one of the most revered practices in Hindu tradition.</p>
            </div>
            """,
            "meta_description": "Learn about Rudrabhishek, the sacred bathing ritual of Lord Shiva. Discover its significance, benefits, and the proper way to perform this powerful puja.",
            "tags": "rudrabhishek,lord shiva,puja rituals,abhishek,shiva lingam,vedic mantras",
            "category_id": 3,  # Puja Rituals
            "is_featured": False,
            "is_active": True,
            "publish_time": datetime.now() - timedelta(days=1),
            "image_url": sample_images[0]
        }
    ]
    
    for i, blog_data in enumerate(blogs_data):
        # Check if blog already exists
        existing = db.query(Blog).filter(Blog.title == blog_data["title"]).first()
        if existing:
            continue
            
        # Download and save image
        image_filename = f"blog-{i+1}-{uuid.uuid4()}.jpg"
        image_path = download_and_save_image(blog_data["image_url"], image_filename)
        
        # Update content to use local image path
        if image_path:
            blog_data["content"] = blog_data["content"].replace(
                f'src="uploads/images/{blog_data["title"].lower().replace(" ", "-")}.jpg"',
                f'src="{image_path}"'
            )
        
        # Remove image_url from blog_data as it's not in the model
        blog_data.pop("image_url", None)
        
        # Generate slug
        slug = blog_data["title"].lower().replace(' ', '-').replace(':', '').replace(',', '')
        import re
        slug = re.sub(r'[^a-z0-9\-]', '', slug)
        blog_data["slug"] = slug
        blog_data["author_id"] = admin_user.id
        
        # Create blog
        blog = Blog(**blog_data)
        db.add(blog)
    
    db.commit()
    print("✅ Dummy blogs created successfully!")

def main():
    """Main function to create dummy data"""
    print("🚀 Starting to create dummy blog data...")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create admin user
        print("👤 Creating admin user...")
        admin_user = create_admin_user(db)
        
        # Create categories
        print("📂 Creating blog categories...")
        categories = create_categories(db)
        
        # Create dummy blogs
        print("📝 Creating dummy blogs with real images...")
        create_dummy_blogs(db, admin_user, categories)
        
        print("🎉 All dummy data created successfully!")
        print("\n📋 Summary:")
        print(f"   - Categories: {len(categories)}")
        print(f"   - Admin user created/verified")
        print(f"   - 5 sample blogs created with real content and images")
        print(f"   - Images downloaded and optimized")
        
        print("\n🔗 You can now access:")
        print("   - GET /api/v1/blogs/ - View all blogs")
        print("   - GET /api/v1/blogs/featured - View featured blogs")
        print("   - GET /api/v1/blogs/categories/ - View categories")
        print("   - http://localhost:8000/docs - API documentation")
        
    except Exception as e:
        print(f"❌ Error creating dummy data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()