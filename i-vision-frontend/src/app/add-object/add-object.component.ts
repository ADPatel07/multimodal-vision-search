import { Component, inject, Inject } from '@angular/core';
import { FormArray, FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { ApiservicesService } from '../apiservices.service';
import { DOCUMENT, TitleCasePipe } from '@angular/common';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';


@Component({
  selector: 'app-add-object',
  imports: [ReactiveFormsModule, MatDialogModule, TitleCasePipe],
  templateUrl: './add-object.component.html',
  styleUrl: './add-object.component.css'
})
export class AddObjectComponent {

  constructor(private apiservices: ApiservicesService, @Inject(DOCUMENT) private document: Document) { }

  fileURL: any
  file: any
  objects: any
  scaleX: any
  scaleY: any
  currentIndex: any

  readonly dialogRef = inject(MatDialogRef<AddObjectComponent>);

  uploadForm: any = new FormGroup({
    category: new FormControl(''),
    objects: new FormArray([])
  })


  cetagories = ['all', 'Animals', 'stationery', 'Birds', 'Reptiles', 'Amphibians', 'Invertebrates', 'Fish', "face", "fashion",
                "furniture", "electronics", "vehicles", "kitchenware", "toys", "sports equipment", "food", "plant",
                "book", "construction materials", "weapons"]

  onFileChange(event: any) {
    this.file = event.target.files[0]
    this.fileURL = URL.createObjectURL(this.file)
  }

  async onURLsubmit(url: any) {

    const res = await fetch(url);
    const blob = await res.blob();
    if (res) this.fileURL = url; this.file = new File([blob], "urlimage", { type: blob.type });

  }

  addObject(val: any) {
    this.apiservices.addImage(val).subscribe((res: any) => { this.dialogRef.close() })
  }

  upload() {

    let obj = this.uploadForm.value

    const reader = new FileReader();

    reader.onload = (e: any) => {
      obj.image = e.target.result.split(',')[1]
      this.addObject(obj)
    };

    reader.readAsDataURL(this.file);

  }


  getCutouts() {

    if (this.uploadForm.value.category && this.file) {

      this.apiservices.getCutouts(this.file, this.uploadForm.value.category).subscribe((res: any) => {
        this.objects = res.map((item: any) => {

          this.uploadForm.get('objects')?.push(this.getNewForm(item.identity, item.object, item.box))

          const [x1, y1, x2, y2] = item.box;

          return {
            ...item,
            scaledBox: [
              x1 * this.scaleX,
              y1 * this.scaleY,
              (x2 - x1) * this.scaleX,
              (y2 - y1) * this.scaleY
            ]
          };
        });

        if (this.objects.length > 0) this.currentIndex = 0

      })
    }
  }

  getNewForm(val: any = '', object_img: any, box: any) {
    return new FormGroup({
      identity: new FormControl(val),
      caption: new FormControl(''),
      object_img: new FormControl(object_img),
      box: new FormControl(box)
    })
  }

  changeForm(index: any) {
    this.currentIndex = index
  }

  removeObject(index: any) {
    this.uploadForm.get('objects')?.removeAt(index)
    this.objects.splice(index, 1)
  }

  changeBorderOnHover() {
    const detectionThumbnails: any = this.document.querySelectorAll(".detection-thumbnail");
    const objectMarkers: any = this.document.querySelectorAll(".object-marker");

    detectionThumbnails.forEach((thumbnail: any, index: any) => {
      thumbnail.addEventListener("mouseenter", () => {
        objectMarkers[index].style.borderWidth = "3px";
        objectMarkers[index].style.boxShadow =
          "0 0 0 2px rgba(255, 255, 255, 0.8)";
      });

      thumbnail.addEventListener("mouseleave", () => {
        objectMarkers[index].style.borderWidth = "2px";
        objectMarkers[index].style.boxShadow = "none";
      });
    });
  }

  onImageLoad(img: HTMLImageElement) {

    this.getCutouts()

    const renderedWidth = img.clientWidth;   // CSS rendered width
    const renderedHeight = img.clientHeight; // CSS rendered height

    const originalWidth = img.naturalWidth;  // Original image width
    const originalHeight = img.naturalHeight; // Original image height

    this.scaleX = renderedWidth / originalWidth;
    this.scaleY = renderedHeight / originalHeight;
  }

}
