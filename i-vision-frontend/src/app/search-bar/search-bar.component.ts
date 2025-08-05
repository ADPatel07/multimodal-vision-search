import { Component, inject, Inject } from '@angular/core';
import { ApiservicesService } from '../apiservices.service';
import { DOCUMENT, TitleCasePipe } from '@angular/common';
import { Router } from '@angular/router';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { AddObjectComponent } from '../add-object/add-object.component';
import { FormsModule } from '@angular/forms';
import { MatExpansionModule } from "@angular/material/expansion";
import { DetailCardComponent } from "../detail-card/detail-card.component";
import { finalize } from 'rxjs';

@Component({
  selector: 'app-search-bar',
  imports: [TitleCasePipe, MatDialogModule, FormsModule, MatExpansionModule, DetailCardComponent],
  templateUrl: './search-bar.component.html',
  styleUrl: './search-bar.component.css'
})
export class SearchBarComponent {

  constructor(private apiservices: ApiservicesService, private rout: Router, @Inject(DOCUMENT) private document: Document) { }
  
  items: any
  searchImgURL: any
  image:any

  scaleX: any
  scaleY: any

  currentObject:any
  text = ""

  isExpanded = false
  isClicked = false

  mockImages:any[] = []
  headerValue:any = undefined

  cetagories = ['all', 'Animals', 'Birds', 'Reptiles', 'Amphibians', 'Invertebrates', 'Fish',"face", "fashion", 
                "furniture", "electronics", "vehicles", "kitchenware", "toys", "sports equipment", "food", "plant", 
                "book", "construction materials", "weapons"]

  category: any = ""

  onSelectionChange(val: any) {
    this.category = val

    if(this.image) this.getCutouts()
  }

  setImage(event: any) {

    this.isExpanded = true

    this.image = event?.target?.files[0]
    this.items = []

    if(this.category) this.getCutouts()

    this.searchImgURL = URL.createObjectURL(this.image)

  }

  getCutouts() {

    this.apiservices.getCutouts(this.image, this.category).subscribe((res: any) => {
      this.items = res.map((item: any) => {
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
    })

  }

  searchImage() {
    let query = {'object':this.currentObject, 'text':this.text, 'category': this.category}  
    this.apiservices.searchImage(query).pipe(finalize(()=>{this.isClicked = true})).subscribe((res: any) => {   
      this.mockImages = res
      this.headerValue = Object.values(this.mockImages)[0][0]
    })
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
    const renderedWidth = img.clientWidth;   // CSS rendered width
    const renderedHeight = img.clientHeight; // CSS rendered height

    const originalWidth = img.naturalWidth;  // Original image width
    const originalHeight = img.naturalHeight; // Original image height

    this.scaleX = renderedWidth / originalWidth;
    this.scaleY = renderedHeight / originalHeight;
  }


  readonly dialog = inject(MatDialog);

  openDialog() {
    this.dialog.open(AddObjectComponent);
  }

}
