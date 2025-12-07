# Paano Himoon nga Permanent ang Images (Cloudinary Setup)

## Ano nga Problema?
Kada mag-hosting ka sa Render, mawala tanan nga images nga gin-upload mo. 
Kailangan naton Cloudinary para ma-save permanent ang images sa cloud.

## Huo-a Lang:

### 1. Create Cloudinary Account (FREE)
1. Adto sa: https://cloudinary.com/users/register_free
2. Sign up gamit email mo
3. Verify email kag login

### 2. Kuha mo ang Credentials
Sa Cloudinary Dashboard, makita mo:
```
Cloud Name: your_cloud_name_here
API Key: 123456789012345
API Secret: abcd123xyz456
```
KOPYA INING TATLO!

### 3. I-add sa Render Environment Variables
1. Adto sa Render Dashboard: https://dashboard.render.com
2. Pili ang "Capstone-System-Final" web service
3. Adto sa **Environment** tab
4. I-add ang TATLO nga environment variables:

```
CLOUDINARY_CLOUD_NAME = your_cloud_name_here
CLOUDINARY_API_KEY = 123456789012345  
CLOUDINARY_API_SECRET = abcd123xyz456
USE_CLOUDINARY = True
```

5. Click "Save Changes"

### 4. Deploy
Mag-auto deploy ang Render. Wait lang 5-10 minutes.

## Paano mo Mahibalan nga Working Na?

### Test 1: Upload Image
1. Login sa admin: https://capstone-system-final.onrender.com/admin/login
2. Adto sa: https://capstone-system-final.onrender.com/appointments/admin/manage-service-images/
3. Upload test image
4. Dapat makita dayon ang image

### Test 2: Check kung Permanent
1. Sa Render Dashboard, i-click "Manual Deploy" → "Deploy latest commit"
2. Wait 5-10 minutes para sa deployment
3. Balik sa service images page
4. DAPAT NANDOON PA RIN ANG IMAGE! ✅

## Ano ang Mahitabo?

### DAAN (Problema):
```
Upload Image → Render Server → ❌ MADULA pag nag-redeploy
```

### SUBONG (Solution):
```
Upload Image → Cloudinary Cloud → ✅ PERMANENT NA!
                     ↓
              Render displays from Cloudinary
```

## Free Tier Limits (Cloudinary)
- Storage: 25 GB (sobra na para sa clinic!)
- Bandwidth: 25 GB/month
- Cost: $0 (LIBRE GIDS!)

## Ano ang Nahuman Ko:

✅ Na-install ko ang Cloudinary packages
✅ Na-configure ko ang settings.py  
✅ Na-create ko ang media folders
✅ May 39 service images na sa database
✅ May 5 product images na sa database

## Ano pa Kulang:

❌ Cloudinary credentials sa Render (IKAW NA ang bahala ani!)
❌ Redeploy sa Render para ma-use ang Cloudinary

## Pagkatapos mo i-setup:

✅ Permanent na tanan images
✅ Indi na mawala bisan pila ka beses mag-redeploy
✅ Makita mo tanan uploaded images sa folder
✅ No need na mag-upload liwat!

---

**IMPORTANTE:** After mo i-add ang Cloudinary credentials, TANAN nga bag-o nga images mag-save automatically sa Cloudinary cloud storage kag INDI NA MADULA! 🎉
