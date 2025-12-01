# Paano I-setup ang Cloudinary para sa Mga Larawan (Tagalog Guide)

## Problema na Nasolusyunan
Sa Render free tier, ang mga na-upload na larawan (service images, product images) ay nawawala pag nag-redeploy kasi ang storage ay temporary lang. Pero ngayon, may Cloudinary na - **LIBRE** at **PERMANENT** ang storage ng mga larawan!

## Ano ang Binago

### 1. Patients - 500 na lang (dating 762)
- Mas mabilis ang system
- Patient IDs: 1 hanggang 500

### 2. Cloudinary - Para sa Larawan
- **Indi na mawala ang mga uploaded images**
- Permanent na kahit mag-redeploy
- Libre lang!

## Hakbang 1: Gumawa ng Cloudinary Account (LIBRE)

1. **Punta sa**: https://cloudinary.com/users/register_free
2. **Mag-sign up** gamit ang email mo (LIBRE!)
3. **I-verify** ang email, then mag-login

## Hakbang 2: Kunin ang Cloudinary Credentials

Pagkatapos mag-login sa Cloudinary:

1. Makikita mo ang **Dashboard**
2. May **Account Details** sa taas:
   ```
   Cloud Name: your_cloud_name
   API Key: 123456789012345
   API Secret: abcdefghijklmnopqrstuvwxyz
   ```
3. **I-copy** ang tatlong values na yan

## Hakbang 3: I-configure sa Render

1. **Punta sa Render Dashboard**: https://dashboard.render.com/
2. **Click** sa `capstone-system-final` (yung web service mo)
3. **Click "Environment"** sa kaliwa
4. **I-add** ang mga environment variables:

   **I-click** ang "Add Environment Variable" at i-lagay ang:

   | Key (Exact name) | Value (Yung kinopy mo) |
   |-----------------|------------------------|
   | `USE_CLOUDINARY` | `True` |
   | `CLOUDINARY_CLOUD_NAME` | (Yung cloud name mo from Cloudinary) |
   | `CLOUDINARY_API_KEY` | (Yung API key mo from Cloudinary) |
   | `CLOUDINARY_API_SECRET` | (Yung API secret mo from Cloudinary) |

5. **Click "Save Changes"** sa baba

## Hakbang 4: I-deploy ang Bagong Code

### Madali lang - Manual Deploy:

1. Sa **Render Dashboard**, punta sa web service mo
2. **Click "Manual Deploy"** button
3. **Click "Deploy latest commit"**
4. **Maghintay** ng 2-5 minutes hanggang matapos

## Hakbang 5: I-test kung Gumana

### Test 1: Patient Limit (500 na lang)
1. **Punta sa**: https://capstone-system-final.onrender.com/appointments/admin/patients/
2. **Tignan**: Dapat **500** na lang ang Total Patients
3. **Check**: Patient IDs ay 1, 2, 3... hanggang 500

### Test 2: Upload ng Larawan (Permanent na!)
1. **Punta sa**: https://capstone-system-final.onrender.com/appointments/admin/manage-service-images/
2. **Mag-upload** ng test image sa kahit anong service
3. **Tignan**: Dapat lumabas ang image
4. **I-redeploy** ulit ang app (Manual Deploy → Deploy latest commit)
5. **Bumalik** sa page ng images
6. **Result**: Dapat **NANDOON PA RIN** ang image! ✅ **INDI NA MAWALA!**

Pareho lang para sa product images:
- https://capstone-system-final.onrender.com/appointments/admin/manage-product-images/

## Ano ang Mangyayari

### Patients
- ✅ 500 na lang ang patients (dating 762)
- ✅ IDs: 1 to 500
- ✅ Mas mabilis ang system

### Mga Larawan (Images)
- ✅ Service images - **PERMANENT NA** (indi na mawala)
- ✅ Product images - **PERMANENT NA** (indi na mawala)
- ✅ Profile pictures - **PERMANENT NA** (indi na mawala)
- ✅ Kahit mag-redeploy - **NANDOON PA RIN ANG MGA LARAWAN!**

## Paano Gumagana

### Dati (May Problema):
```
Upload Image → Render Server → ❌ MAWAWALA pag nag-redeploy
```

### Ngayon (May Solution na!):
```
Upload Image → Cloudinary Cloud → ✅ PERMANENT! INDI NA MAWALA!
                     ↓
              Render ay kukuha lang from Cloudinary
```

## Cloudinary Libre (Free) - Limits

Huwag mag-alala, sobrang laki ng limits:
- **Storage**: 25 GB (sobra-sobra na yan para sa clinic)
- **Bandwidth**: 25 GB/month
- **Bayad**: **₱0.00** - WALANG BAYAD! 100% LIBRE!

## Kung May Problema

### Hindi maka-upload ng images?
1. Check kung tama ang environment variables sa Render
2. Verify kung tama ang Cloudinary credentials
3. Tignan ang Render logs: Dashboard → Logs

### Nawawala pa rin ang dating images?
- **Normal lang yan** - yung dating images ay sa temporary storage pa
- **Solution**: I-upload ulit ang importante na images - PERMANENT NA SILA NGAYON!

### Parang local storage pa rin?
- Check kung `USE_CLOUDINARY=True` sa Render environment variables
- I-redeploy after mag-add ng environment variables

## Buod (Summary)

### Mga Binago na Files
1. ✅ `accounts/management/commands/limit_patients.py` - 500 patients na
2. ✅ `build.sh` - 500 patients limit
3. ✅ `requirements.txt` - May Cloudinary packages na
4. ✅ `settings.py` - Configured na ang Cloudinary

### Ano ang Dapat Gawin Ngayon
1. ✅ Gumawa ng Cloudinary account (LIBRE!)
2. ✅ I-add ang environment variables sa Render
3. ✅ I-deploy ang updated code
4. ✅ I-test ang patient limit (500 na dapat)
5. ✅ I-test ang image upload (PERMANENT NA!)

---

## IMPORTANTE! ⚠️

**Pagkatapos ng lahat ng steps:**
- Lahat ng i-upload mo na images = **PERMANENT NA**
- Kahit mag-redeploy ng 100 beses = **NANDOON PA RIN ANG IMAGES**
- **INDI NA MAWALA** = GUARANTEED! 🎉

**LIBRE LANG LAHAT!** No hidden charges, 100% free ang Cloudinary free tier!
